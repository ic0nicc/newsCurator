from sklearn.cluster import DBSCAN
import numpy as np

def cluster_articles(embeddings):

  embeddings = np.array(embeddings)

  clustering = DBSCAN(
      eps=0.30,
      min_samples=2,
      metric="cosine"
  )

  labels = clustering.fit_predict(embeddings)

  return labels