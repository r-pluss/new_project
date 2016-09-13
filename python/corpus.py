#creating a large body of data from existing open data sources 

import bs4
import redis
import requests

#initial data source
url = "https://www.wikidata.org/w/index.php?title=Special:WhatLinksHere/Property:P570&limit=500"

wiki_page = requests.get(url)
if not wiki_page.ok:
    raise ValueError('Unable to get initial data from wikidata.org - {0} : {1}'.format(wiki_page.status_code, wiki_page.reason))
html = bs4.BeautifulSoup(wiki_page.content, 'lxml')
for item in hmtl.find(id = 'mw-whatlinkshere-list').find_all('li'):
    link = item.find('a').get('href')
    process(link)
    
    
def process(url):
    wiki_page = requests.get("https://www.wikidata.org{0}".format(url))
    if not wiki_page.ok:
        raise ValueError('Unable to get initial data from wikidata.org - {0} : {1}'.format(wiki_page.status_code, wiki_page.reason))
    html = bs4.BeautifulSoup(wiki_page.content, 'lxml')
    #get the date of death
    death_date = html.find(id = 'P570').find(class_ = 'wikibase-snakview-value').contents[0]
    if death_date is None:
        return
    else:
        #get the common name for the person
        who_is = html.find(class_ = 'wikibase-title-label').text.strip()
        #get the general description
        descript = html.find(class_ = 'wikibase-entitytermsview-heading-description').text.strip()
        #check for occupation properties to include as metadata
        jobs = [item.text.strip() for item in
            html.find(id = 'P106').find_all(class_ = 'wikibase-statementview-mainsnak')
        ]
        #see if there's an image to use
        img_url = html.find(id = 'P18').find('a', class_ = 'extiw')['href']
        if img_url[0:2] == '//':
            img_url = 'http:' += img_url
        #get the link for the person's wikipedia entry
        wiki_link = html.find(class_ = 'wikibase-entityview-side').find('a', hreflang = 'en')['href']
        #try to generate a ranking index value
        #number of inter-wiki links will be used as a proxy for notoriety
        wiki_page_main = requests.get(wiki_link)
        if not wiki_page_main.ok:
            return
        main_html = bs4.BeautifulSoup(wiki_page_main.content, 'lxml')
        links_url = 'https://en.wikipedia.org' + main.html.find(id = 't-whatlinkshere').find('a')['href'] + "?limit=2000"
        wiki_links_page = requests.get(links_url)
        if not wiki_links_page.ok:
            return
        
        
        
