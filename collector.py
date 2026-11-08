from flask import Flask
from database import db
from article_db import add_article, article_exists, get_latest_articles
from news_api import get_news
from rss_news import get_rss_news
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "newsCurator" / "instance" / "news.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH.as_posix()}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

import models


def save_articles(articles):
    saved = 0
    skipped = 0

    for article in articles:
        if not article["url"]:
            continue

        if article_exists(article["url"]):
            skipped += 1
            continue

        if not article["content"]:
            continue

        publication_date = article["publication_date"]

        if isinstance(publication_date, str):
            try:
                publication_date = datetime.fromisoformat(
                    publication_date.replace("Z", "+00:00")
                )
            except ValueError:
                publication_date = datetime.now()

        if publication_date is None:
            publication_date = datetime.now()

        add_article(
            title=article["title"],
            url=article["url"],
            source_name=article["source_name"],
            publication_date=publication_date,
            content=article["content"],
            category=article["category"]
        )

        saved += 1

    return saved, skipped


def collect_news():
    print("Collecting news from NewsAPI...")
    news_api_articles = get_news()

    print("Collecting news from RSS feeds...")
    rss_articles = get_rss_news()

    all_articles = (
        news_api_articles
        + rss_articles
    )

    print("\nTotal articles collected:", len(all_articles))

    saved, skipped = save_articles(all_articles)

    print("Articles saved:", saved)
    print("Duplicates skipped:", skipped)


def display_articles():
    articles = get_latest_articles(20)
    print("\n" + "=" * 100)
    print("DAILY NEWS AGENT")
    print("=" * 100)
    number = 1
    for article in articles:
        content = article.content
        if len(content) > 500:
            content = content[:500] + "..."
        print("\nArticle", number)
        print("-" * 100)
        print("Title:", article.title)
        print("Source:", article.source_name)
        print("Category:", article.category)
        print("Published:", article.publication_date)
        print("URL:", article.url)
        print("\nContent:")
        print(content)
        print("-" * 100)
        number += 1


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        collect_news()
        display_articles()