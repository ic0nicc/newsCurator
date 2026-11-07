Further improvement scope:

A. Don't cluster unrelated time periods together
Suppose an article about Google's AI announcement was published six months ago.

Another article about a new Google AI model is published today.

They might have high semantic similarity, but they could describe completely different events.

Therefore, consider publication time when clustering.

For example:
- Cluster articles collected within the same daily window.
- Compare articles from the previous 24–48 hours.
- Retain older clusters for historical reference.
Eventually, you can introduce temporal similarity into your clustering logic.

B. DBSCAN can suffer from chaining
Consider three articles:
- A is similar to B.
- B is similar to C.
- A is not particularly similar to C.
DBSCAN can still put all three into the same cluster because density connectivity can connect them indirectly.

This is a potential problem for news deduplication.

Later, you can investigate:
- Agglomerative clustering with average linkage.
- Graph-based clustering.
- Additional pairwise similarity validation within clusters.
Don't try to solve every edge case in your first implementation.

C. Don't confuse semantic similarity with event identity
This is particularly important for your project.

Consider:
- Google releases Gemini.
- Google announces a new AI research facility.
- Google invests in an AI startup.
All three articles are semantically related to Google and AI.

But they describe three different events.

A sentence embedding model captures semantic relationships, not guaranteed event identity.

For better event-level clustering, you can eventually combine:
1. Title embeddings.
2. Article content embeddings.
3. Named entity information.
4. Publication time.
5. Pairwise similarity thresholds.
This will help distinguish articles discussing the same event from articles merely discussing the same subject.