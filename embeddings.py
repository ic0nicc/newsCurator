
from sentence_transformers import SentenceTransformer
from article_db import get_all_articles
from database import db
import numpy as np

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

    titles=[]
    contents=[]

    for article in missing_articles:

        titles.append(article.title or "")
        contents.append((article.content or "")[:500])

    title_embeddings = model.encode(
        titles,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )
    content_embeddings = model.encode(
        contents,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )    

    embeddings = (
        0.65*title_embeddings +
        0.35*content_embeddings
    )
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / np.maximum(norms, 1e-12)

    for article, embedding in zip(
        missing_articles, embeddings
    ):

        article.embedding = embedding.tolist()

    db.session.commit()

    print("New embeddings generated:", len(missing_articles))
