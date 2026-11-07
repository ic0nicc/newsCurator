from collector import app
from database import db
from article_db import get_all_articles
from embeddings import generate_embeddings
from clustering import cluster_articles
import numpy as np

with app.app_context():

  articles = get_all_articles()

  if not articles:
    print("No articles found")
    exit()

  missing = [
    article for article in articles
    if article.embedding is None
  ]

  if missing:
    generate_embeddings()
    articles = get_all_articles()

  embeddings = np.array([
    article.embedding for article in articles
  ])

  labels = cluster_articles(embeddings)

  for article, label in zip(articles, labels):

    article.cluster_label = int(label)

  db.session.commit()

  clusters = {}

  for article, label in zip(articles, labels):

    if label == -1:
      continue

    clusters.setdefault(int(label), []).append(article)

  for cluster_id, cluster_articles_list in clusters.items():

    print(f"\nCLUSTER {cluster_id}")

    for article in cluster_articles_list:

      print(article.title)
      print(article.source_name)

  print("\nTotal clusters:", len(clusters))
  print("Independent articles:", np.sum(labels == -1))