import feedparser
from datetime import datetime
from articlecontent import extract_article, classify_article


RSS_FEEDS = {
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "NASA": "https://www.nasa.gov/rss/dyn/breaking_news.rss"
}


def get_rss_news():
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

            content = extract_article(article_url) ## extract articles is a function of trafilatura

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

    return news