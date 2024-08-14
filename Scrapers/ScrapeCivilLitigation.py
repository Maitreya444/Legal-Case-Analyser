import feedparser
from newspaper import Article
import re
import os

# Replace with the actual RSS feed URLs you found
rss_urls = [
    'https://www.civillitigationbrief.com/feed/',
    'https://www.civillitigationbrief.com/search/costs/feed/rss2/'
]

def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    if feed.bozo == 0:  # Checking if the feed was parsed without errors
        print(f"Feed Title: {feed.feed.title}")
        print(f"Feed Link: {feed.feed.link}")
        print("--------")
        for entry in feed.entries:
            sanitized_title = sanitize_filename(entry.title)
            filename = f"CivilLitigationBriefArticles/{sanitized_title}.txt"
            if not os.path.exists(filename):
                print(f"Title: {entry.title}")
                print(f"Link: {entry.link}")
                print(f"Published: {entry.published}")
                print("--------")
                fetch_article_content(entry.link, entry.title, entry.published)
            else:
                print(f"Article already exists: {filename}")
    else:
        print(f"Failed to parse RSS feed from {url}")

def sanitize_filename(filename):
    # Remove invalid characters for filenames
    return re.sub(r'[^a-zA-Z0-9_\- ]', '', filename).replace(' ', '_')

def fetch_article_content(url, title, published_date):
    try:
        article = Article(url)
        article.download()
        article.parse()
        print(f"Full Article Title: {article.title}")
        #print(f"Full Article Summary: {article.text[:200]}...")
        print("--------")

        # Sanitize the title to create a valid filename
        sanitized_title = sanitize_filename(title)
        filename = f"CivilLitigationBriefArticles/{sanitized_title}.txt"

        # Ensure the summary directory exists
        os.makedirs('CivilLitigationBriefArticles', exist_ok=True)

        # Write the article content to a text file
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
