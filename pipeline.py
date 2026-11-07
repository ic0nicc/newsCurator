
import numpy as np

from collector import app
from database import db
from article_db import get_all_articles
from embeddings import generate_embeddings
from clustering import cluster_articles
from summarization import summarize_cluster


def run_curation_pipeline():

    with app.app_context():

        print("\nStarting news curation pipeline...")

        articles = get_all_articles()

        if not articles:
            return {
                "status": "empty",
                "message": "No articles available for processing."
            }

        print("\nStep 1: Generating embeddings...")

        missing_embeddings = [
            article for article in articles
            if article.embedding is None
        ]

        if missing_embeddings:
            generate_embeddings()

        articles = get_all_articles()

        if any(article.embedding is None for article in articles):
            raise RuntimeError("Some articles are missing embeddings.")

        print("\nStep 2: Clustering articles...")

        embeddings = np.asarray(
            [article.embedding for article in articles],
            dtype=np.float32
        )

        labels = cluster_articles(embeddings)

        for article, label in zip(articles, labels):
            article.cluster_label = int(label)

        db.session.commit()

        clusters = sorted(set(int(label) for label in labels))

        normal_clusters = [
            label for label in clusters if label != -1
        ]

        independent_articles = int(np.sum(labels == -1))

        print("Total clusters:", len(normal_clusters))
        print("Independent articles:", independent_articles)

        print("\nStep 3: Generating summaries...")

        curated_stories = []

        for cluster_id in clusters:

            result = summarize_cluster(cluster_id)

            if result is None:
                continue

            if cluster_id == -1:

                for item in result["summaries"]:

                    curated_stories.append({
                        "cluster_label": -1,
                        "article_count": 1,
                        "summary": item["summary"],
                        "sources": [
                            {
                                "title": item["title"],
                                "source": item["source"],
                                "url": item["url"]
                            }
                        ]
                    })

            else:
                curated_stories.append(result)

        print("\nNews curation completed.")

        return {
            "status": "success",
            "total_articles": len(articles),
            "total_clusters": len(normal_clusters),
            "independent_articles": independent_articles,
            "total_stories": len(curated_stories),
            "stories": curated_stories
        }
