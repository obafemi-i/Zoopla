import requests
import pandas as pd
from selectolax.parser import HTMLParser

from urllib.parse import urljoin
from string import ascii_lowercase as asc

import os
import re

import creds


output = 'output.csv'

session = requests.Session()

scraped_urls_file = 'scraped_urls.txt'


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


def get_link(url):
    html = get_html(url)
    body = html.css('ul.clearfix li')

    for bod in body:
        link = bod.css_first('a').attributes['href']
        full_link = urljoin('https://www.zoopla.co.uk/', link)

        yield full_link


def get_scraped_urls():
    try:
        with open(scraped_urls_file, 'r') as file:
            scraped_urls = set(file.read().splitlines())
    except FileNotFoundError:
        scraped_urls = set()

    return scraped_urls


def parse_attribute_error(html, selector):
    try:
        data = html.css_first(selector).text().strip()
        return re.sub(r'\s+', ' ', data)

    except AttributeError:
        return None
    

def export_to_csv(ads: list):
    file_exists = os.path.isfile(output)

    output_df = pd.DataFrame(ads)

    if not file_exists:
        output_df.to_csv(output, index=False)  
    else:
        output_df.to_csv(output, mode='a', header=False, index=False)


def extract_and_save_info(url):
    links = get_link(url)

    for link in links:

        # to avoid scraping an already scraped URL incase the scraper has to be restarted
        if link in get_scraped_urls():
            print(f"Skipping {link} as it has already been scraped.")
            continue

        main = get_html(link)

        address = parse_attribute_error(main, 'div.agents-results-copy p span').split('-')[0]
        contacts = parse_attribute_error(main, 'div.agents-results-contact-item.agents-results-contact-phone a')
        name = parse_attribute_error(main, 'div#content h1')

        agent_list = []

        agent_dict = {
           'Agency': name,
           'Contact': contacts,
           'Address': address
        }

        agent_list.append(agent_dict)

        export_to_csv(agent_list)

        # Add the scraped URL to the set of scraped URLs
        get_scraped_urls().add(link)

        # Save the scraped URLs to the file
        with open(scraped_urls_file, 'a') as file:
            file.write(link + '\n')

        print(f'Details of {name} agency extracted, moving on...')


def main():
    for alf in asc:
        url_scrape = f'https://www.zoopla.co.uk/find-agents/estate-agents/directory/{alf}/'
        extract_and_save_info(url_scrape)


if __name__ == '__main__':
    main()