Agno Agent
    |
    v
collect_all_news()
    |
    v
NewsAPI collection
    |
    v
RSS collection
    |
    v
Save new articles to SQLite
    |
    v
run_curation_pipeline()
    |
    +----> Generate missing embeddings
    |
    +----> Run DBSCAN
    |
    +----> Store cluster labels
    |
    +----> Summarise each cluster
    |
    v
Return curated stories to Agno
    |
    v
Agent presents the results

Further Improvements:

1 Currently, we're clustering all articles again whenever   the pipeline runs.
That is reasonable for a dataset of a few hundred articles. Later, we can introduce incremental clustering, nearest-neighbour retrieval and FAISS.

2 Scheduled collection:
The system collects and curates news automatically every morning, even when nobody interacts with the agent.
We can use APScheduler. 