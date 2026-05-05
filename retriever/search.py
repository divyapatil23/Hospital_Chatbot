from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import numpy as np
import os

load_dotenv()

client     = MongoClient(os.getenv("MONGODB_URI"))
collection = client["hospital"]["patients"]
embedder   = SentenceTransformer("BAAI/bge-small-en-v1.5")

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)) 

def search_patients(query: str) -> list:
    query_vector = embedder.encode(query).tolist()

    # Fetch all records that have embeddings
    all_docs = list(collection.find(
        {"embedding": {"$exists": True}},
        {
            "text_chunk":             1,
            "embedding":              1,
            "primary_diagnosis":      1,
            "treatment_type":         1,
            "age":                    1,
            "gender":                 1,
            "readmission_risk_score": 1
        }
    ))
    # Score every document against the query
    scored = []
    for doc in all_docs:
        score = cosine_similarity(query_vector, doc["embedding"])
        scored.append((score, doc))

    # Sort by score, return top 5
    scored.sort(key=lambda x: x[0], reverse=True)
    top5 = [doc for _, doc in scored[:5]]
    return top5