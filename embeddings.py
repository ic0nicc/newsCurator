
from sentence_transformers import SentenceTransformer
from article_db import get_all_articles
from database import db


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def generate_embeddings():

    articles = get_all_articles()

    missing_articles = [
        article for article in articles
        if article.embedding is None
    ]

    if not missing_articles:
        print("All articles already have embeddings.")
        return

    texts = []

    for article in missing_articles:

        text = (
            article.title + ". " +
            article.content[:1500]
        )

        texts.append(text)

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    for article, embedding in zip(
        missing_articles, embeddings
    ):

        article.embedding = embedding.tolist()

    db.session.commit()

    print("New embeddings generated:", len(missing_articles))
