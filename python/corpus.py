#creating a large body of data from existing open data sources 

import bs4
import redis
import requests

#initial data source
url = "https://www.wikidata.org/w/index.php?title=Special:WhatLinksHere/Property:P570&limit=500"

wiki_page = requests.get(url)
if not wiki_page.ok:
    raise ValueError('Unable to get initial data from wikidata.org - {0} : {1}'.format(wiki_page.status_code, wiki_page.reason))
html = bs4.BeautifulSoup(wiki_page.content, 'html.parser')
for item in hmtl.find(id = 'mw-whatlinkshere-list').find_all('li'):
    link = item.find('a').get('href')
    process(link)
    
    
def process(url):
    wiki_page = requests.get("https://www.wikidata.org{0}".format(url))
    if not wiki_page.ok:
        raise ValueError('Unable to get initial data from wikidata.org - {0} : {1}'.format(wiki_page.status_code, wiki_page.reason))
    html = bs4.BeautifulSoup(wiki_page.content, 'html.parser')
    #get the date of death
    death_date = html.find(id = 'P570').find(class_ = 'wikibase-snakview-value').contents[0]