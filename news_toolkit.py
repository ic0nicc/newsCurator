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

URL = "https://newsapi.org/v2/top-headlines"

PARAMS = {
    "country": "us",
    "pageSize": 5
}

HEADERS = {
    "X-Api-Key": API_KEY
}

RSS_FEEDS = {
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "NASA": "https://www.nasa.gov/rss/dyn/breaking_news.rss"
}


class NewsToolkit(Toolkit):

    def __init__(self, **kwargs):

        tools = [
            self.collect_all_news
        ]

        instructions = (
            "Use collect_all_news whenever the user requests news collection. "
            "This tool collects news from both NewsAPI and RSS feeds. "
            "It extracts, classifies, and saves articles to the database. "
            "Preserve article titles, URLs, and source names when reporting news. "
            "Report the collection statistics accurately."
        )

        super().__init__(
            name="news_toolkit",
            tools=tools,
            instructions=instructions,
            add_instructions=True,
            **kwargs
        )

    def collect_all_news(self):
        """
        Collect news from both NewsAPI and RSS feeds.
        Return combined collection statistics.
        """

        news_api_result = {
            "articles": [],
            "saved_to_database": 0,
            "skipped": 0
        }

        rss_result = {
            "articles": [],
            "saved_to_database": 0,
            "skipped": 0
        }

        errors = []

        try:
            news_api_result = self.get_news()
        except Exception as e:
            errors.append(f"NewsAPI error: {str(e)}")

        try:
            rss_result = self.get_rss_news()
        except Exception as e:
            errors.append(f"RSS error: {str(e)}")

        api_articles = news_api_result.get("articles", [])
        rss_articles = rss_result.get("articles", [])

        all_articles = api_articles + rss_articles
        
        processing_result = None
        try:

            print("\nStarting automated processing...")

            from pipeline import run_curation_pipeline

            processing_result = run_curation_pipeline()

        except Exception as e:

            errors.append(
                f"Processing pipeline error: {str(e)}"
            )
            
        return {
        "total_collected": len(all_articles),

        "total_saved": (
            news_api_result.get("saved_to_database", 0)
            + rss_result.get("saved_to_database", 0)
        ),

        "total_skipped": (
            news_api_result.get("skipped", 0)
            + rss_result.get("skipped", 0)
        ),

        "news_api_count": len(api_articles),
        "rss_count": len(rss_articles),

        "articles": [
            {
                "title": article["title"],
                "source": article["source_name"],
                "category": article["category"],
                "url": article["url"]
            }
            for article in all_articles
        ],

        "curation": processing_result,

        "errors": errors
    }

    def get_news(self):
        """
        Fetch top headlines from NewsAPI.
        Extract, classify, and save articles.
        """

        response = requests.get(
            URL,
            params=PARAMS,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        articles = data.get("articles", [])

        news = []

        for article in articles:

            title = article.get("title")
            article_url = article.get("url")
            source_name = article.get("source", {}).get("name")
            publication_date = article.get("publishedAt")
            description = article.get("description")

            if not article_url:
                continue

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

    def get_rss_news(self):
        """
        Fetch news from configured RSS feeds.
        Extract, classify, and save articles.
        """

        news = []

        for source_name, feed_url in RSS_FEEDS.items():

            feed = feedparser.parse(feed_url)

            for entry in feed.entries:

                title = entry.get("title")
                article_url = entry.get("link")
                description = entry.get("summary", "")

                if not article_url:
                    continue

                publication_date = None

                if entry.get("published_parsed"):
                    publication_date = datetime(
                        *entry.published_parsed[:6]
                    )

                elif entry.get("updated_parsed"):
                    publication_date = datetime(
                        *entry.updated_parsed[:6]
                    )

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
