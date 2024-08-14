import feedparser
from newspaper import Article
import re
import os

# Replace with the actual RSS feed URLs you found
rss_urls = [
    'https://costsbarrister.co.uk/feed/'
]

# File to store titles of scrapped articles
SCRAPPED_CB_ARTICLES_FILE = 'scrapped_articles_costbarrister.txt'

# Function to load scrapped articles from the file
def load_scrapped_articles():
    if os.path.exists(SCRAPPED_CB_ARTICLES_FILE):
        with open(SCRAPPED_CB_ARTICLES_FILE, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file)
    return set()

# Function to save scrapped article title to the file
def save_scrapped_article(title):
    with open(SCRAPPED_CB_ARTICLES_FILE, 'a', encoding='utf-8') as file:
        file.write(title + '\n')

def fetch_rss_feed(url):
    scrapped_articles = load_scrapped_articles()
    feed = feedparser.parse(url)
    if feed.bozo == 0:  # Checking if the feed was parsed without errors
        print(f"Feed Title: {feed.feed.title}")
        print(f"Feed Link: {feed.feed.link}")
        print("--------")
        for entry in feed.entries:
            sanitized_title = sanitize_filename(entry.title)
            if sanitized_title not in scrapped_articles:
                print(f"Title: {entry.title}")
                print(f"Link: {entry.link}")
                print(f"Published: {entry.published}")
                print("--------")
                fetch_article_content(entry.link, entry.title, entry.published)
                save_scrapped_article(sanitized_title)
            else:
                print(f"Article already exists: {sanitized_title}")
    else:
        print(f"Failed to parse RSS feed from {url}")

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_\- ]', '', filename).replace(' ', '_')

def fetch_article_content(url, title, published_date):
    try:
        article = Article(url)
        article.download()
        article.parse()
        print(f"Full Article Title: {article.title}")
        print("-------------")
        # sanitizing the title to create a valid filename
        sanitized_title = sanitize_filename(title)
        filename = f"CostBarristerArticles/{sanitized_title}.txt"
        os.makedirs('CostBarristerArticles', exist_ok=True)
        
        # writing the article content to a text file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Title: {article.title}\n")
            file.write(f"Published Date: {published_date}\n\n")
            file.write(article.text)
            file.write(article.url)
        print(f"Article saved as {filename}")
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

for url in rss_urls:
    fetch_rss_feed(url)
