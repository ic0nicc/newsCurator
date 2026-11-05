from flask import Flask, render_template
from database import db
import models
from article_db import get_latest_articles,get_article_by_id

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///news.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    articles = get_latest_articles(20)

    return render_template(
        "index.html",
        articles=articles
    )
@app.route("/article/<int:article_id>")

def article(article_id):
    article = get_article_by_id(article_id)

    if article is None:
        return "Article not found", 404

    return render_template(
        "article.html",
        article=article
    )

if __name__ == "__main__":
    app.run(debug=True)