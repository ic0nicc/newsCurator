import os
import requests
import feedparser

from datetime import datetime
from dotenv import load_dotenv
from agno.tools.toolkit import Toolkit
from articlecontent import extract_article, classify_article
from collector import app, save_articles


load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")

url = "https://newsapi.org/v2/top-headlines"

params = {
    "apiKey": API_KEY,
    "country": "us",
    "pageSize": 5
}

RSS_FEEDS = {
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "NASA": "https://www.nasa.gov/rss/dyn/breaking_news.rss"
}


class NewsToolkit(Toolkit):
    def __init__(self, **kwargs):
        tools = [
            self.get_news,
            self.get_rss_news
        ]

        instructions = (
            "Use get_news to fetch the configured NewsAPI top headlines. "
            "Use get_rss_news to fetch articles from the configured RSS feeds. "
            "Both tools extract, classify, and save articles to the database. "
            "Their results contain the articles, saved_to_database count, "
            "and skipped count. "
            "Preserve the returned URLs and source names when summarising news."
        )

        super().__init__(
            name="news_toolkit",
            tools=tools,
            instructions=instructions,
            add_instructions=True,
            **kwargs
        )

    def get_news(self):
        """
        Fetch top headlines from NewsAPI.

        Fetch news, extract and classify articles,
        save them to the database, and return the
        articles along with database insertion statistics.
        """
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print("Error:", response.json())
            return []

        data = response.json()

        articles = data.get("articles", [])

        news = []

        for article in articles:
            title = article.get("title")
            article_url = article.get("url")
            source_name = article.get("source", {}).get("name")
            publication_date = article.get("publishedAt")
            description = article.get("description")

            content = extract_article(article_url)
            ##this classification task will be done by the transformer...
            category = classify_article(
                title or "",
                description or ""
            )

            news.append({
                "title": title,
                "url": article_url,
                "source_name": source_name,
                "publication_date": publication_date,
                "content": content,
                "category": category
            })

        saved, skipped = self.save_to_database(news)
        return {
            "articles": news,
            "saved_to_database": saved,
            "skipped": skipped
        }

    def get_rss_news(self):
        """
        Fetch news from the configured RSS feeds.

        Returns a list of article dictionaries containing title, URL,
        source name, publication date, extracted content, and category.
        """
        news = []

        for source_name, feed_url in RSS_FEEDS.items():
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                title = entry.get("title")
                article_url = entry.get("link")
                description = entry.get("summary", "")

                publication_date = None

                if entry.get("published_parsed"):
                    publication_date = datetime(*entry.published_parsed[:6])

                elif entry.get("updated_parsed"):
                    publication_date = datetime(*entry.updated_parsed[:6])

                content = extract_article(article_url)

                category = classify_article(
                    title or "",
                    description or ""
                )

                news.append({
                    "title": title,
                    "url": article_url,
                    "source_name": source_name,
                    "publication_date": publication_date,
                    "content": content,
                    "category": category
                })

        saved, skipped = self.save_to_database(news)

        return {
            "articles": news,
            "saved_to_database": saved,
            "skipped": skipped
        }
    def save_to_database(self, news):
        from database import db
        with app.app_context():
            db.create_all()
            saved, skipped = save_articles(news)

        return saved, skipped
