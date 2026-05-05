import streamlit as st
from pipeline.chatbot import chat

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title = "Hospital Patient Chatbot",
    page_icon  = "🏥",
    layout     = "centered"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    .source-pill {
        display: inline-block;
        background: #e8f4fd;
        color: #1a73e8;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.title("🏥 Hospital Patient Chatbot")
st.caption("Answers strictly from 8,000 patient records · Groq LLaMA 3.3 · MongoDB")
st.divider()

# ── Build history for memory ──────────────────────────────
def build_history() -> list:
    history = []
    messages = st.session_state.get("messages", [])
    for i in range(0, len(messages) - 1, 2):
        if (i + 1 < len(messages)
                and messages[i]["role"] == "user"
                and messages[i+1]["role"] == "assistant"):
            history.append({
                "question": messages[i]["content"],
                "answer":   messages[i+1]["content"],
                "query":    messages[i+1].get("query", "")
            })
    return history

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💡 Example Questions")
    st.markdown("Click any question to ask it:")

    examples = [
        "What are the types of primary diagnosis?",
        "What are the types of insurance?",
        "Which is the most occurred primary diagnosis?",
        "What is the most common insurance type?",
        "How many patients are male?",
        "How many surgeries have been performed?",
        "What is the maximum length of stay?",
        "Which patients have the highest readmission risk?",
        "What is the diagnosis of patient P00398?",
        "How many patients have Diabetes in the South region?",
        "What is the average age of Heart Failure patients?",
        "How many uninsured patients have Sepsis?",
        "Which region has the most patients?",
        "How many patients stayed more than 10 days?",
        "What is the average readmission risk score?",
    ]

    for ex in examples:
        if st.button(ex, use_container_width=True, key=ex):
            st.session_state["clicked_question"] = ex

    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown("""
    - **Database**: MongoDB (local)
    - **Records**: 8,000 patients
    - **LLM**: Groq LLaMA 3.3 70B
    - **Mode**: Deterministic (temp=0)
    - **Agent**: Dynamic MongoDB queries
    - **Memory**: Full conversation history
    """)

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# ── Chat history init ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ── Welcome message on first load ─────────────────────────
if len(st.session_state["messages"]) == 0:
    with st.chat_message("assistant"):
        st.markdown("""
👋 Hello! I'm your **Hospital Patient Chatbot**.

I query **8,000 real patient records** from MongoDB to answer your questions.

I remember your conversation — so you can ask follow-up questions like:
- *"How many male patients have Diabetes?"*
- *"Who are those patients?"*
- *"What is their average age?"*

Type your question below or click one from the sidebar! 👇
        """)

# ── Display previous messages ─────────────────────────────
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("patients", 0) > 0:
            st.markdown(
                f'<div class="source-pill">📊 Based on {msg["patients"]} patient record(s)</div>',
                unsafe_allow_html=True
            )

# ── Handle sidebar button click ───────────────────────────
if "clicked_question" in st.session_state:
    question = st.session_state.pop("clicked_question")

    st.session_state["messages"].append({
        "role":    "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Querying patient database..."):
            result = chat(question, history=build_history())

        st.markdown(result["answer"])

        if result.get("patients", 0) > 0:
            st.markdown(
                f'<div class="source-pill">📊 Based on {result["patients"]} patient record(s)</div>',
                unsafe_allow_html=True
            )

    st.session_state["messages"].append({
        "role":     "assistant",
        "content":  result["answer"],
        "patients": result.get("patients", 0),
        "query":    result.get("query", "")
    })

    st.rerun()

# ── Chat input box ────────────────────────────────────────
if question := st.chat_input("Ask anything about the patient database..."):

    st.session_state["messages"].append({
        "role":    "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Querying patient database..."):
            result = chat(question, history=build_history())

        st.markdown(result["answer"])

        if result.get("patients", 0) > 0:
            st.markdown(
                f'<div class="source-pill">📊 Based on {result["patients"]} patient record(s)</div>',
                unsafe_allow_html=True
            )

    st.session_state["messages"].append({
        "role":     "assistant",
        "content":  result["answer"],
        "patients": result.get("patients", 0),
        "query":    result.get("query", "")
    })

    st.rerun()