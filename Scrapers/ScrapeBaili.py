import requests
from bs4 import BeautifulSoup
import csv
import os

URL = "https://www.bailii.org/recent-decisions.html#ew/cases/EWHC/Costs"
SPECIFIC_TITLE = 'England and Wales High Court (Senior Courts Costs Office) Decisions'

CSV_FILE = 'Baili_links.csv'
LOG_FILE = 'scrape_baili_log.txt'
SCRAPED_LINKS_FILE = 'scraped_links.txt'
ARTICLE_DIR = 'BailiArticles'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def load_scraped_links(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file)
    return set()

def scrape_website(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

def find_links(soup, specific_title):
    h3_tags = soup.find_all('h3')
    for h3 in h3_tags:
        if h3.text.strip() == specific_title:
            ul = h3.find_next('ul')
            if ul:
                return [(link.text.strip(), link['href']) for link in ul.find_all('a', href=True)]
    return []

def write_to_csv(filepath, links):
    file_exists = os.path.isfile(filepath)
    with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        if not file_exists:
            csv_writer.writerow(['name', 'link'])
        for name, link in links:
            csv_writer.writerow([name, link])

def write_to_log(filepath, links):
    with open(filepath, 'a', encoding='utf-8') as logfile:
        for name, link in links:
            logfile.write(f"Text: {name}, URL: {link}\n")

def save_new_links(filepath, new_links):
    with open(filepath, 'a', encoding='utf-8') as file:
        for _, link_url in new_links:
            file.write(f"{link_url}\n")

def save_articles(new_links):
    if not os.path.exists(ARTICLE_DIR):
        os.makedirs(ARTICLE_DIR)

    for name, link_url in new_links:
        full_url = "https://www.bailii.org" + link_url
        response = requests.get(full_url, headers=HEADERS)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html5lib')
            body_content = soup.body.get_text(strip=True)

            # Create a filename from the link text
            filename = f"{ARTICLE_DIR}/{name[:50].replace(' ', '_').replace('/', '_')}.txt"

            # Save the article content to a text file
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(body_content)
        else:
            print(f"Failed to retrieve the article. Status code: {response.status_code}, URL: {full_url}")

def main():
    scraped_links = load_scraped_links(SCRAPED_LINKS_FILE)
    soup = scrape_website(URL)
    if soup:
        links = find_links(soup, SPECIFIC_TITLE)
        new_links = [(name, link) for name, link in links if link not in scraped_links]

        if new_links:
            write_to_csv(CSV_FILE, new_links)
            write_to_log(LOG_FILE, new_links)
            save_new_links(SCRAPED_LINKS_FILE, new_links)
            save_articles(new_links)

            print(f"New links found: {new_links}")
        else:
            print("No new links found.")

if __name__ == "__main__":
    main()
