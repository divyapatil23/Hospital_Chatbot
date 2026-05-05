from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a hospital data analyst assistant.

YOUR STRICT RULES:
1. Answer ONLY using the patient records given to you.
2. NEVER make up information or use your own knowledge.
3. If the answer is not in the records, say exactly:
   "I don't have enough data in the database to answer this."
4. Always mention how many patients your answer is based on.
5. Be concise, factual, and professional.
"""

def ask_groq(question: str, patient_records: list) -> str:

    # Build context and join them from multiple retrieved patient records
    context = "\n\n---\n\n".join([
        doc["text_chunk"] for doc in patient_records
    ])

    user_message = f"""
Here are the relevant patient records from the database:

{context}

---
Question: {question}

Answer strictly based on the patient records above only.
"""

    response = client.chat.completions.create(
        model       = "llama-3.3-70b-versatile",
        temperature = 0.0,
        messages    = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ]
    )

    return response.choices[0].message.content