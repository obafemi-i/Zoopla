import requests
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import creds

url_scrape = 'https://www.zoopla.co.uk/find-agents/estate-agents/directory/a/'

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'}

session = requests.Session()

def get_html(url_to_scrape):

    response = session.get(
    url='https://proxy.scrapeops.io/v1/',

    params={
      'api_key': creds.api_key,
      'url': url_to_scrape, 
        },
    )
    html = HTMLParser(response.content)

    return html


def get_link():
    html = get_html(url_scrape)
    body = html.css('ul.clearfix li')

    for bod in body:
        link = bod.css_first('a').attributes['href']
        full_link = urljoin('https://www.zoopla.co.uk/', link)

        yield full_link

links = get_link()

for link in links:
    main = get_html(link)
    data = main.css_first('div.agents-results-copy').text()
    print(data)

