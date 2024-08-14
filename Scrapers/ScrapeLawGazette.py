import newspaper
import feedparser
from newspaper import Article
import os
import re

def scrape_news_from_feed(url):
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            try:
                article = newspaper.Article(entry.link)
                article.download()
                article.parse()
                article.nlp()
                articles.append({
                    'title': article.title or 'No Title',
                    'author': article.authors or ['Unknown'],
                    'publish_date': article.publish_date or 'No Date',
                    'content': article.text or 'No Content',
                    'link': article.canonical_link or entry.link
                })
            except Exception as e:
                print(f"Error processing article from {entry.link}: {e}")
    except Exception as e:
        print(f"Error parsing feed from {url}: {e}")
    return articles

def sanitize_filename(filename):
    # Removing characters that are not allowed in filenames
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)[:255]

def save_to_directory(article, output_directory, log_file_path, processed_files):
    sanitized_title = sanitize_filename(article['title'])
    file_name = os.path.join(output_directory, f"{sanitized_title}.txt")

    # Ensure the article is not already processed
    if sanitized_title in processed_files:
        print(f"Article '{sanitized_title}' has already been processed.")
        return

    try:
        print(f"Saving article '{sanitized_title}' to {file_name}")

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(f"Title: {article['title']}\n")
            file.write(f"Author: {', '.join(article['author'])}\n")
            file.write(f"Publish Date: {article['publish_date']}\n")
            file.write(f"Link: {article['link']}\n\n")
            file.write(article['content'])
        
        # Log the processed file
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{sanitized_title}\n")

    except Exception as e:
        print(f"Error saving article '{sanitized_title}': {e}")

def main():
    rss_urls = [
        'https://www.lawgazette.co.uk/7137.rss', 
        'https://www.lawgazette.co.uk/7105.rss',
        'https://www.lawgazette.co.uk/7096.rss',
        'https://www.lawgazette.co.uk/7118.rss',
        'https://www.lawgazette.co.uk/6392.rss'
    ]

    output_directory = r'C:\Users\DELL\OneDrive\Desktop\FINAL\LawGazetteArticles'
    log_file_path = os.path.join(output_directory, 'processed_lawgazette_summary.log')

    all_articles = []

    for url in rss_urls:
        articles = scrape_news_from_feed(url)
        all_articles.extend(articles)

    print(f"Total articles fetched: {len(all_articles)}")

    processed_files = set()
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            processed_files = set(log_file.read().splitlines())

    for article in all_articles:
        save_to_directory(article, output_directory, log_file_path, processed_files)

if __name__ == "__main__":
    main()
