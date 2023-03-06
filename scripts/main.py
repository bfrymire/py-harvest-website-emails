import click
import re
import csv
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

import requests
from requests.compat import urlparse
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@click.command()
@click.option('--input', '--i', type=str, help='CSV file that holds list of websites to harvest')
@click.option('--max-pages', '--p', default=300, type=int, help='maximum number of pages to walk')
@click.option('--max-emails', '--e', default=20, type=int, help='maximum number email addresses to harvest')
@click.option('--max-time', '--t', default=-1, type=int, help='maximum amount of time to harvest each website in seconds')
@click.option('--verbosity', '--v', default=2, type=int, help='verbosity of output')
@click.option('--wait-time', '--w', default=1000, type=int, help='time to wait in milliseconds')
def harvest_website_emails(input, max_pages, max_emails, max_time, verbosity, wait_time):
    verbosity = clamp(verbosity, 0, 2)
    delta = timedelta(seconds=max_time)
    website_urls = get_websites_from_csv(input)
    level = 0
    results = []
    program_start_time = datetime.now()
    p = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    service = Service(ChromeDriverManager().install())
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gup')
    options.add_argument('--disable-infobars')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--disable-extensions')
    options.add_argument('--incognito')
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    for url in website_urls:
        start_time = datetime.now()
        base_url = urlparse(url).netloc
        result = {
            'websites': url,
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
            if index > 0:
                time.sleep(wait_time / 1000)
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
            # Selenium is unable to get the status code of the request, so we use requests here for that
            r = requests.head(link)
            # Skip if we don't get a good response
            if not r.ok:
                status = f'Skipping, got status code: {r.status_code}'
                if index == 1:
                    result['status'] = status
                harvest_print(status, level=level+1)
                continue
            driver.get(link)
            time.sleep(3)
            soup = bs(driver.page_source, 'html.parser')
            body = soup.find('body')
            # Skip if the link doesn't have a body tag
            if not body:
                status = 'Skipping, HTML <body> not found'
                if index == 1:
                    result['status'] = status
                harvest_print(status, level=level+1)
                continue
            if verbosity == 2:
                harvest_print(f'Harvesting links from current url: {r.url}', level=level)
            print(body)
            # TODO: fix not getting the URL of href if it starts with '#'
            a_links = [x['href'] for x in body.find_all('a', href=True) if urlparse(x['href']).netloc == base_url]
            print(a_links)
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
                # Remove mailto links from the email address
                mailto = "mailto:"
                mailto_len = len(mailto)
                if email.startswith(mailto):
                    email = email[mailto_len:]
                # Check for duplicate email
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
    if verbosity == 2:
        print('Closing browser session')
    driver.quit()

def get_websites_from_csv(fname):
    if not Path(fname).exists():
        create_websites_csv(fname)
        print(f'Exiting program.')
        quit()
    with open(fname) as f:
        reader = csv.DictReader(f)
        return [x['websites'] for x in reader]

def create_websites_csv(fname='example.csv'):
    if Path(fname).exists():
        action = 'already exists'
    else:
        action = 'created'
        with open(fname, 'w') as f:
            f.write('websites,\n')
    print(f'CSV file {fname} {action}. Populate "websites" column with your URLs.')

def within_allocated_time(delta):
    return datetime.now() <= delta

def harvest_print(text, level=0, indent="  "):
    print(f'{indent*level}{text}')

def clamp(n, a, b):
    return min(max(n, min(a, b)), max(a, b))

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
