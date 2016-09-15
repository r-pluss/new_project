#creating a large body of data from existing open data sources 

import bs4
import datetime
import re
#import redis
import requests

test_limit = 30

def process(url):
    wiki_page = requests.get("https://www.wikidata.org{0}".format(url))
    if not wiki_page.ok:
        raise ValueError('Unable to get data from wikidata.org - {0} : {1}'.format(wiki_page.status_code, wiki_page.reason))
    html = bs4.BeautifulSoup(wiki_page.content, 'lxml')
    #get the date of death
    try:
        death_date = html.find(id = 'P570').find(class_ = 'wikibase-snakview-value').contents[0]
    except AttributeError:
        return
    #get the birthdate
    try:
        birthdate = html.find(id = 'P569').find(class_ = 'wikibase-snakview-value').contents[0]
    except AttributeError:
        return
    #get the common name for the person
    who_is = html.find(class_ = 'wikibase-title-label').text.strip()
    #get the general description
    descript = html.find(class_ = 'wikibase-entitytermsview-heading-description').text.strip()
    #check for occupation properties to include as metadata
    try:
        jobs = [item.text.strip() for item in
            html.find(id = 'P106').find_all(class_ = 'wikibase-statementview-mainsnak')
        ]
    except AttributeError:
        jobs = []
    #see if there's an image to use
    img_url = html.find(id = 'P18').find('a', class_ = 'extiw')['href']
    if img_url[0:2] == '//':
        img_url = 'http:' + img_url
    #get the link for the person's wikipedia entry
    wiki_link = html.find(class_ = 'wikibase-entityview-side').find('a', hreflang = 'en')['href']
    #try to generate a ranking index value
    #number of inter-wiki links will be used as a proxy for notoriety
    wiki_page_main = requests.get(wiki_link)
    if not wiki_page_main.ok:
        return
    main_html = bs4.BeautifulSoup(wiki_page_main.content, 'lxml')
    links_url = 'https://en.wikipedia.org' + main_html.find(id = 't-whatlinkshere').find('a')['href'] + "?limit=3000"
    wiki_links_page = requests.get(links_url)
    if not wiki_links_page.ok:
        return
    wiki_links_html = bs4.BeautifulSoup(wiki_links_page.content, 'lxml')
    link_count = len(wiki_links_html.find(id = 'mw-whatlinkshere-list').find_all('li'))
    return {
        'name': who_is,
        'born': birthdate,
        'died': death_date,
        'description': descript,
        'occupations': jobs,
        'image_url': img_url,
        'fame': link_count
    }

def persist(data):
    #further process the data and, if it meets criteria, save to redis keystore
    pass

def convert_date(date):
    formats = ['%d %B %Y']
    for f in formats:
        try:
            d = datetime.datetime.strptime(date, f)
            return datetime.date(d.year, d.month, d.day)
        except ValueError:
            pass
    raise ValueError('{0} is not in accepted format.'.format(date))
    
def lifespan_days(born, died):
    return (died - born).days

def gather_data(html):
    for item in html.find(id = 'mw-whatlinkshere-list').find_all('li'):
        if len(test_results) >= test_limit:
            break
        link = item.find('a').get('href')
        data = process(link)
        if data is not None:
            try:
                data['days_alive'] = lifespan_days(convert_date(data['born']), convert_date(data['died']))
                test_results.append(data)
            except ValueError:
                pass
            
def get_next_page(html):
    url = "https://wikidata.org{0}".format(
        html.find(id = 'mw-content-text').find('a', string = re.compile("next\s[0-9]+")).get('href')
    )
    page = requests.get(url)
    if page.ok:
        return bs4.BeautifulSoup(page.content, 'lxml')
    else:
        raise ValueError('Unable to get additional data - {0} : {1}'.format(page.status_code, page.reason))

#initial data source
url = "https://www.wikidata.org/w/index.php?title=Special:WhatLinksHere/Property:P570&limit=500"


wiki_page = requests.get(url)
if not wiki_page.ok:
    raise ValueError('Unable to get initial data from wikidata.org - {0} : {1}'.format(wiki_page.status_code, wiki_page.reason))
html = bs4.BeautifulSoup(wiki_page.content, 'lxml')

#for testing only, will be removed soon
test_results = []

gather_data(html)
while(len(test_results) < test_limit):
    html = get_next_page(html)
    gather_data(html)

