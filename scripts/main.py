import click
import re
import csv
import json
from pathlib import Path
from datetime import datetime, timedelta

import requests
from requests.compat import urlparse
from bs4 import BeautifulSoup as bs

@click.command()
def cli():
    """Example script."""
    click.echo('Hello World!')

''' Why reinvent the wheel? Using regex from https://ihateregex.io/expr/email
p = '[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+ '
 '''
@click.command()
@click.option('--input', '--i', type=str, help='CSV file that holds list of websites to harvest')
@click.option('--max-pages', '--p', default=300, type=int, help='maximum number of pages to walk')
@click.option('--max-emails', '--e', default=20, type=int, help='maximum number email addresses to harvest')
@click.option('--max-time', '--t', default=60*5, type=int, help='maximum amount of time to harvest each website in seconds')
@click.option('--verbosity', '--v', default=2, type=int, help='maximum amount of time to harvest each website in seconds')
def harvest_website_emails(input, max_pages, max_emails, max_time, verbosity):
    delta = timedelta(seconds=max_time)
    website_urls = get_websites_from_csv(input)
    results = []
    print(website_urls)
    p = re.compile('[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+')
    for url in website_urls:
        start_time = datetime.now()
        base_url = urlparse(url).netloc
        links = [url]
        emails = []
        index = 0
        print(f'Starting to harvest site: {base_url}')
        while index < len(links):
            if index >= max_pages:
                print(f'Reached maximum webpages to step into')
                break
            if not within_allocated_time(start_time + delta):
                print(f'Reached maximum time allocated to harvest website')
                break
            if len(emails) >= max_emails:
                print(f'Reached maximum number of email addresses to harvest')
                break
            link = links[index]
            r = requests.get(link)
            if r.status_code == 200:
                # Preparing soup
                soup = bs(r.text, 'html.parser')
                body = soup.find('body')
                if verbosity == 2:
                    print(f'Harvesting links from current url: {r.url}')
                tags = [x['href'] for x in body.find_all('a', href=True) if urlparse(x['href']).netloc == base_url]
                for tag in tags:
                    if tag not in links:
                        links.append(tag)
                if verbosity == 2:
                    print(f'Harvesting emails from {r.url}')
                matches = re.findall('[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+', body.text)
                for match in matches:
                    if match not in emails:
                        emails.append(match)
                        print(match)
            else:
                print(f'Got status code: {r.status_code}')
            index += 1
        end_time = datetime.now()
        total_time = end_time - start_time
        results.append({
            'website': url,
            'start_time': start_time,
            'end_time': end_time,
            'total_time': total_time,
            'base_url': base_url,
            'emails': emails,
            'links': links,
        })
    with open('../results.json', 'w') as f:
        f.write(json.dumps(results, cls=DateTimeEncoder))

def get_websites_from_csv(fname):
    if not Path(fname).exists():
        print(f'Exiting program - file does not exist: {fname}')
        quit()
    with open(fname) as f:
        reader = csv.DictReader(f)
        return [x['website'] for x in reader]

def within_allocated_time(delta):
    return datetime.now() <= delta

'''
Class for dumping dict with datetime or timedelta classes to string
https://stackoverflow.com/a/56562567
'''
class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime) or isinstance(z, timedelta):
            return (str(z))
        else:
            return super().default(z)

if __name__ == '__main__':
    harvest_website_emails()
