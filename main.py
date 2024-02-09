import requests
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import creds
import os
import pandas as pd

url_scrape = 'https://www.zoopla.co.uk/find-agents/estate-agents/directory/a/'

output = 'output.csv'

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'}

session = requests.Session()

def get_html(url_to_scrape: str):

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


def parse_attribute_error(html, selector):
    try:
        return html.css_first(selector).text().strip()
    except AttributeError:
        return None
    

def export_to_csv(ads: list):
    file_exists = os.path.isfile(output)

    output_df = pd.DataFrame(ads)

    if not file_exists:
        output_df.to_csv(output, index=False)  
    else:
        output_df.to_csv(output, mode='a', header=False, index=False)


links = get_link()

for link in links:
    main = get_html(link)

    address = parse_attribute_error(main, 'div.agents-results-copy p')
    contacts = parse_attribute_error(main, 'div.agents-results-contact-item.agents-results-contact-phone a')
    name = parse_attribute_error(main, 'div#content h1')

