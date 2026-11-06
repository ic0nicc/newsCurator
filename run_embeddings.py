from collector import app
from database import db
from embeddings import generate_embeddings

with app.app_context():
  generate_embeddings()