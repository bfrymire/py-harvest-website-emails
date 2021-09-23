import pathlib
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


@click.command()
@click.option('--input', '--i', type=str, help='CSV file that holds list of websites to harvest')
@click.option('--max-pages', '--p', default=300, type=int, help='maximum number of pages to walk')
@click.option('--max-emails', '--e', default=20, type=int, help='maximum number email addresses to harvest')
@click.option('--max-time', '--t', default=-1, type=int, help='maximum amount of time to harvest each website in seconds')
@click.option('--verbosity', '--v', default=2, type=int, help='verbosity of output')
def harvest_website_emails(input, max_pages, max_emails, max_time, verbosity):
    verbosity = clamp(verbosity, 0, 2)
    delta = timedelta(seconds=max_time)
    website_urls = get_websites_from_csv(input)
    level = 0
    results = []
    program_start_time = datetime.now()
    p = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    for url in website_urls:
        start_time = datetime.now()
        base_url = urlparse(url).netloc
        result = {
            'website': url,
            'start_time': start_time,
            'base_url': base_url,
        }
        links = [url]
        exclude_links = []
        emails = []
        index = -1
        harvest_print(f'Starting to harvest site: {base_url}', level=level)
        level += 1
        while True:
            index += 1
            if index >= len(links):
                status = 'Reached end of harvested links'
                result['status'] = status
                harvest_print(status, level=level)
                break
            if max_pages >= 0 and index >= max_pages:
                status = 'Reached maximum webpages to step into'
                result['status'] = status
                harvest_print(status, level=level)
                break
            if max_time >= 0 and not within_allocated_time(start_time + delta):
                status = 'Reached maximum time allocated to harvest website'
                result['status'] = status
                harvest_print(status, level=level)
                break
            if max_emails >= 0 and len(emails) >= max_emails:
                status = 'Reached maximum number of email addresses to harvest'
                result['status'] = status
                harvest_print(status, level=level)
                break
            link = links[index]
            r = requests.get(link)
            # Skip if we don't get a good response
            if r.status_code != 200:
                harvest_print(f'Skipping, got status code: {r.status_code}', level=level+1)
                continue
            soup = bs(r.text, 'html.parser')
            body = soup.find('body')
            # Skip if the link doesn't have a body tag
            if not body:
                harvest_print('Skipping, HTML <body> not found', level=level+1)
                continue
            if verbosity == 2:
                harvest_print(f'Harvesting links from current url: {r.url}', level=level)
            a_links = [x['href'] for x in body.find_all('a', href=True) if urlparse(x['href']).netloc == base_url]
            new_links = 0
            for a_link in a_links:
                if a_link not in links and a_link not in exclude_links:
                    new_links += 1
                    links.append(a_link)
                    if verbosity == 2:
                        harvest_print(f'{a_link}', level=level+1)
            if verbosity == 2:
                if new_links:
                    harvest_print(f'{new_links} new links found', level=level+1)
                else:
                    harvest_print('No new links found', level=level+1)
            if verbosity == 2:
                harvest_print(f'Harvesting emails from {r.url}', level=level)
            found_emails = []
            matches = re.findall(p, body.text)
            found_emails += matches
            mailto_links = [x['href'] for x in body.find_all(href=True) if x['href'].startswith('mailto:')]
            
            matches = re.findall(p, body.text)
            found_emails += mailto_links
            new_emails = 0
            for email in found_emails:
                if email not in emails:
                    new_emails += 1
                    emails.append(email)
                    harvest_print(email, level=level+1)
            if verbosity == 2:
                if new_emails:
                    harvest_print(f'{new_emails} new emails found', level=level+1)
                else:
                    harvest_print('No new emails found', level=level+1)
        result['total_time'] = datetime.now() - start_time
        result['emails'] = emails
        result['links'] = links
        results.append(result)
    level -= 1
    with open('results.json', 'w') as f:
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

def harvest_print(text, level=0, indent="  "):
    print(f'{indent*level}{text}')

def clamp(n, minimum, maximum):
    return max(minimum, min(n, maximum))

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
