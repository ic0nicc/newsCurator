def classify_article(title, description):
    text = (title + " " + (description or "")).lower()

    if any(word in text for word in ["technology", "tech", "software", "ai", "artificial intelligence", "computer", "robot"]):
        return "Technology"

    if any(word in text for word in ["science", "research", "space", "nasa", "physics", "biology"]):
        return "Science"

    if any(word in text for word in ["business", "market", "stock", "economy", "company", "finance"]):
        return "Business"

    if any(word in text for word in ["sport", "football", "cricket", "basketball", "tennis", "soccer"]):
        return "Sports"

    if any(word in text for word in ["politics", "election", "president", "senate", "government"]):
        return "Politics"

    if any(word in text for word in ["movie", "film", "music", "celebrity", "entertainment", "actor"]):
        return "Entertainment"

    if any(word in text for word in ["health", "medical", "doctor", "hospital", "disease"]):
        return "Health"

    return "World"