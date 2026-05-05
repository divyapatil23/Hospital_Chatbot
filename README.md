# Hospital Patient Chatbot

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-ff4b4b?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange)](https://groq.com/)
[![LLaMA](https://img.shields.io/badge/LLaMA-3.3%2070B-purple)](https://groq.com/)
[![Sentence Transformers](https://img.shields.io/badge/Sentence--Transformers-Embeddings-green)](https://www.sbert.net/)

Hospital Patient Chatbot is a Streamlit-based AI chatbot that answers natural-language questions about hospital patient records stored in MongoDB. It uses Groq's LLaMA model to convert user questions into MongoDB queries, execute them on the patient database, and format the result into a clear answer.

## Project Overview

The chatbot allows users to ask questions such as:

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
Streamlit app receives the question
        |
        v
pipeline/chatbot.py checks greeting vs database question
        |
        v
db/agent.py asks Groq to generate a MongoDB query
        |
        v
MongoDB executes the query on patient records
        |
        v
Groq formats the raw result into a readable answer
        |
        v
Streamlit displays the answer
```

Example:

```text
Question: How many male patients are there?
```

The model generates a MongoDB-style query:

```json
{
  "operation": "count",
  "filter": {
    "gender": "Male"
  }
}
```

MongoDB returns the count, and the chatbot displays the final answer.

## Project Structure

```text
chatbot/
├── app.py
├── .env
├── config/
│   └── settings.py
├── db/
│   ├── agent.py
│   ├── add_embeddings.py
│   └── hospital_readmission_dataset.csv
├── llm/
│   └── groq_chat.py
├── pipeline/
│   └── chatbot.py
├── retriever/
│   └── search.py
├── test_agent.py
├── test_chatbot.py
├── test_connection.py
└── debug.py
```

## Important Files

### `app.py`

Creates the Streamlit chatbot interface. It displays the title, sidebar example questions, chat history, input box, and final answers.

### `pipeline/chatbot.py`

Acts as the middle layer. It checks whether the user message is a greeting or a real database question. Greetings are answered directly, while database questions are sent to the agent.

### `db/agent.py`

Main intelligence layer. It uses Groq to generate MongoDB queries from natural-language questions, executes those queries, and formats the result into a readable answer.

### `db/add_embeddings.py`

Creates text summaries and embeddings for patient records. This supports semantic search.

### `retriever/search.py`

Searches patient records by meaning using cosine similarity between embeddings.

### `llm/groq_chat.py`

Generates answers from already-retrieved patient records. This belongs to the alternate retrieval-based flow.

### `.env`

Stores private configuration values such as:

```text
GROQ_API_KEY=your_groq_api_key
MONGODB_URI=your_mongodb_connection_string
```

Do not commit this file to GitHub.

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

Activate it:

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

### 5. Make Sure MongoDB Is Running

The chatbot expects patient records in:

```text
Database: hospital
Collection: patients
```

### 6. Run the App

```bash
streamlit run app.py
```

## Optional: Generate Embeddings

If you want to use semantic search, run:

```bash
python db/add_embeddings.py
```

This adds `text_chunk` and `embedding` fields to patient records.

## Testing

Test Groq and MongoDB connections:

```bash
python test_connection.py
```

Test the chatbot pipeline:

```bash
python test_chatbot.py
```

Test the database agent:

```bash
python test_agent.py
```

## Security Notes

- Never commit `.env`.
- Never commit API keys.
- Do not upload `venv/` to GitHub.
- If an API key was exposed, regenerate it from the provider dashboard.

## Badge Buttons

The clickable buttons at the top of this README are Markdown image links using Shields.io.

Example:

```markdown
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
```

Structure:

```text
[![Button Text](Badge Image URL)](Clickable Link URL)
```

So:

- `Badge Image URL` creates the colored badge.
- `Clickable Link URL` decides where the badge opens when clicked.

## License

This project is for educational and demonstration purposes.
