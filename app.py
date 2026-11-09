from flask import Flask, render_template
from database import db
import models
from article_db import get_latest_articles,get_article_by_id
import json
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "instance" / "news.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH.as_posix()}"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
DIGEST_PATH = Path(__file__).with_name("daily_digest.json")
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    articles = get_latest_articles(40)
    digest = None

    if DIGEST_PATH.exists():
        with open(DIGEST_PATH, "r", encoding="utf-8") as file:
            digest = json.load(file)

    return render_template(
        "index.html",
        articles=articles,
        digest=digest
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