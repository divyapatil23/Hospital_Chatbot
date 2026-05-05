from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

client     = MongoClient(os.getenv("MONGODB_URI"))
collection = client["hospital"]["patients"]
model      = SentenceTransformer("BAAI/bge-small-en-v1.5")

# Only process records that don't have embeddings yet
records = list(collection.find({"embedding": {"$exists": False}}))
print(f"⏳ Adding embeddings to {len(records)} patient records...")


for i, doc in enumerate(records):

    # Build a plain English summary of each patient
    # This is what the chatbot will search through
    text = f"""
Patient {doc.get('patient_id', 'Unknown')}:
Age {doc.get('age', 'N/A')}, {doc.get('gender', 'N/A')} from {doc.get('region', 'N/A')} region.
Admitted in {doc.get('season', 'N/A')} season on {doc.get('admission_date', 'N/A')}.
Primary diagnosis: {doc.get('primary_diagnosis', 'N/A')}.
Treatment type: {doc.get('treatment_type', 'N/A')}.
Length of stay: {doc.get('length_of_stay', 'N/A')} days.
Number of comorbidities: {doc.get('comorbidities_count', 'N/A')}.
Number of medications: {doc.get('medications_count', 'N/A')}.
Follow-up visits last year: {doc.get('followup_visits_last_year', 'N/A')}.
Previous readmissions: {doc.get('prev_readmissions', 'N/A')}.
Insurance type: {doc.get('insurance_type', 'N/A')}.
Discharge disposition: {doc.get('discharge_disposition', 'N/A')}.
Readmission risk score: {doc.get('readmission_risk_score', 'N/A')}.
""".strip()

    # Convert text to numbers (embedding vector)
    embedding = model.encode(text).tolist()

    # Save back to MongoDB
    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "text_chunk": text,
            "embedding":  embedding
        }}
    )

    # Show progress every 500 records
    if (i + 1) % 500 == 0:
        print(f"   ✅ Done {i+1} / {len(records)} patients")

print(f"\n All embeddings added successfully!")
client.close()