from db.agent import run_agent

# ── Greeting detector ─────────────────────────────────────
def is_greeting(question: str) -> bool:
    greetings = [
        "hello", "hi", "hey", "good morning", "good evening",
        "good afternoon", "how are you", "what can you do",
        "who are you", "help", "thanks", "thank you",
        "bye", "goodbye", "what do you know"
    ]
    q = question.lower().strip()
    return any(q.startswith(g) or q == g for g in greetings)

# ── Greeting responder ────────────────────────────────────
def answer_greeting(question: str) -> dict:
    q = question.lower().strip()

    if any(w in q for w in ["bye", "goodbye", "thank"]):
        return {
            "answer":   "Goodbye! Feel free to return anytime. 👋",
            "patients": 0
        }

    if any(w in q for w in ["what can you do", "who are you", "help"]):
        return {
            "answer": """I'm your **Hospital Patient Chatbot** 🏥

Ask me ANYTHING about 8,000 patient records:
- *"How many male patients?"*
- *"Average age of diabetes patients?"*
- *"Which region has the most patients?"*
- *"How many patients stayed more than 10 days?"*
- *"Who has the highest readmission risk?"*
- *"How many uninsured patients have Sepsis?"*
- *"What is the average length of stay for surgical patients?"*
- *"Tell me about patient P00398"*

I query the **live MongoDB database** for every answer! 💬""",
            "patients": 0
        }

    return {
        "answer":   "Hello! 👋 I'm your Hospital Patient Chatbot.\n\n"
                    "Ask me anything about **8,000 patient records** "
                    "in your MongoDB database!\n\n"
                    "Try: *'How many patients have Diabetes?'*",
        "patients": 0
    }

# ── Main chat function — accepts history for memory ───────
def chat(question: str, history: list = []) -> dict:

    # Empty question guard
    if not question.strip():
        return {
            "answer":   "Please type a question!",
            "patients": 0
        }

    # Handle greetings locally — no DB needed
    if is_greeting(question):
        return answer_greeting(question)

    # Everything else → Agent queries MongoDB dynamically
    return run_agent(question, history)