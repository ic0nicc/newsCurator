import requests
import os
from dotenv import load_dotenv
from articlecontent import extract_article, classify_article

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")

url = "https://newsapi.org/v2/top-headlines"

params = {
    "apiKey": API_KEY,
    "country": "us",
    "pageSize": 5
}


def get_news():
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