from sentence_transformers import SentenceTransformer
from article_db import get_all_articles
from database import db

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

def generate_embeddings():

    articles = get_all_articles()

    if not articles:
        print("No articles found")
        return

    texts = []

    for article in articles:

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

    for article, embedding in zip(articles, embeddings):

        article.embedding = embedding.tolist()

    db.session.commit()

    print("Embeddings generated:", len(articles))