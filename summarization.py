
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from models import Article
from database import db
from collector import app


MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_summary(text):

  prompt = (
    "Summarize the following news information. "
    "Include the most important facts and developments. "
    "Do not invent facts or add external information. "
    "Preserve important disagreements between reports.\n\n"
    + text
  )

  inputs = tokenizer(
    prompt,
    return_tensors="pt",
    truncation=True,
    max_length=512
  )

  outputs = model.generate(
    **inputs,
    max_new_tokens=120,
    num_beams=4,
    no_repeat_ngram_size=3,
    early_stopping=True
  )

  summary = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
  )

  return summary


def split_into_chunks(text, chunk_size=400):
  token_ids = tokenizer.encode(
    text,
    add_special_tokens=False
  )

  chunks = []

  for i in range(0, len(token_ids), chunk_size):

    chunk_ids = token_ids[i:i + chunk_size]

    chunk = tokenizer.decode(
      chunk_ids,
      skip_special_tokens=True
    )

    chunks.append(chunk)

  return chunks



def summarize_cluster(cluster_label):

  with app.app_context():

    articles = Article.query.filter_by(
      cluster_label=cluster_label
    ).all()

    if not articles:
      print("No articles found")
      return None

    # Handle noise articles individually
    if cluster_label == -1:

      results = []

      for article in articles:

        summary = generate_summary(
            article.title + ". " + article.content
        )
        results.append({
          "article_id": article.id,
          "title": article.title,
          "summary": summary,
          "source": article.source_name,
          "url": article.url
        })

      return {
        "cluster_label": -1,
        "article_count": len(articles),
        "summaries": results
      }

    # Handle normal clusters
    combined_text = ""

    for article in articles:

      combined_text += (
        f"\nSource: {article.source_name}\n"
        f"Title: {article.title}\n"
        f"Content: {article.content}\n"
      )

    chunks = split_into_chunks(combined_text)

    intermediate_summaries = []

    for chunk in chunks:

      summary = generate_summary(chunk)

      intermediate_summaries.append(summary)

    final_input = "\n".join(intermediate_summaries)

    final_summary = generate_summary(final_input)

    return {
      "cluster_label": cluster_label,
      "article_count": len(articles),
      "summary": final_summary,
      "sources": [
          {
            "title": article.title,
            "source": article.source_name,
            "url": article.url
          }
          for article in articles
      ]
    }
