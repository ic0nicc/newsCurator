from database import db
from models import Article
from datetime import datetime


def add_article(title, url, source_name, publication_date, content, category):
    article = Article(
        title=title,
        url=url,
        source_name=source_name,
        publication_date=publication_date,
        content=content,
        category=category,
        collected_at=datetime.now()
    )

    db.session.add(article)
    db.session.commit()

    return article


def get_all_articles():
    return Article.query.all()


def get_article_by_id(article_id):
    return db.session.get(Article, article_id)


def get_article_by_url(url):
    return Article.query.filter_by(url=url).first()


def article_exists(url):
    return Article.query.filter_by(url=url).first() is not None


def get_articles_by_category(category):
    return Article.query.filter_by(category=category).all()


def get_articles_by_source(source_name):
    return Article.query.filter_by(source_name=source_name).all()


def get_latest_articles(limit=10):
    return Article.query.order_by(
        Article.publication_date.desc()
    ).limit(limit).all()


def update_article(article_id, title=None, content=None, category=None):
    article = db.session.get(Article, article_id)

    if article is None:
        return None

    if title is not None:
        article.title = title

    if content is not None:
        article.content = content

    if category is not None:
        article.category = category

    db.session.commit()

    return article


def delete_article(article_id):
    article = db.session.get(Article, article_id)

    if article is None:
        return False

    db.session.delete(article)
    db.session.commit()

    return True