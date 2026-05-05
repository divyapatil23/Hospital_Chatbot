from dotenv import load_dotenv
import os

load_dotenv()

# --- API Keys ---
GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
MONGODB_URI     = os.getenv("MONGODB_URI")

# --- Database ---
DB_NAME         = "hospital"          
COLLECTION_NAME = "patients_data"    
VECTOR_INDEX    = "vector_index"

# --- Models ---
GROQ_MODEL      = "llama-3.3-70b-versatile"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# --- Chatbot Behaviour ---
TEMPERATURE     = 0.0   # 0 = same answer every time
TOP_K           = 5     # fetch 5 patient records per question
