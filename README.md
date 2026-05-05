# Hospital Patient Chatbot

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-ff4b4b?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange)](https://groq.com/)
[![LLaMA](https://img.shields.io/badge/LLaMA-3.3%2070B-purple)](https://groq.com/)
[![Sentence Transformers](https://img.shields.io/badge/Sentence--Transformers-Embeddings-green)](https://www.sbert.net/)

Hospital Patient Chatbot is a Streamlit-based AI chatbot that answers natural-language questions about hospital patient records stored in MongoDB. It uses Groq's LLaMA model to convert user questions into MongoDB queries, execute them on the patient database, and format the result into a readable answer.

## Project Overview

The chatbot can answer questions such as:

- How many male patients are there?
- What are the types of insurance?
- Which region has the most patients?
- What is the diagnosis of patient P00398?
- How many diabetic patients are from the South region?
- Which patients have the highest readmission risk?

The system is designed to answer from database records instead of giving general medical advice.

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** MongoDB
- **LLM Provider:** Groq
- **Main Model:** LLaMA 3.3 70B
- **Embeddings:** Sentence Transformers
- **Vector Model:** BAAI/bge-small-en-v1.5

## How It Works

```text
User asks a question
        |
        v
app.py receives the question in the Streamlit UI
        |
        v
pipeline/chatbot.py checks whether it is a greeting or a database question
        |
        v
db/agent.py asks Groq to generate a MongoDB query
        |
        v
MongoDB executes the query on patient records
        |
        v
Groq formats the raw database result into a readable answer
        |
        v
app.py displays the answer in the chat interface
```

Example:

```text
Question: How many male patients are there?
```

Groq generates a MongoDB-style query:

```json
{
  "operation": "count",
  "filter": {
    "gender": "Male"
  }
}
```

MongoDB returns the count, and the chatbot displays the final answer.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hospital-patient-chatbot.git
cd hospital-patient-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install streamlit pymongo python-dotenv groq sentence-transformers numpy
```

### 4. Create `.env`

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key
MONGODB_URI=mongodb://localhost:27017/hospital_db
```

### 5. Start MongoDB

The chatbot expects patient records in:

```text
Database: hospital
Collection: patients
```

### 6. Run the App

```bash
streamlit run app.py
```

## Security Notes

- Never commit `.env`.
- Never commit API keys.
- Do not upload `venv/` to GitHub.
- If an API key was exposed, regenerate it from the provider dashboard.

## License

This project is for educational and demonstration purposes.
