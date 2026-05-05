from groq    import Groq
from pymongo import MongoClient
from dotenv  import load_dotenv
import os, json, re

load_dotenv()

client     = Groq(api_key=os.getenv("GROQ_API_KEY"))
collection = MongoClient(
    os.getenv("MONGODB_URI")
)["hospital"]["patients"]

# ── Database schema descriotion of db to groq
DB_SCHEMA = """
MongoDB collection: hospital → patients
Total documents: 8000

Fields and possible values:
- patient_id               : string  e.g. "P00001"
- admission_date           : date
- season                   : string  ["Spring","Summer","Fall","Winter"]
- age                      : number  (18-90)
- gender                   : string  ["Male","Female"]
- region                   : string  ["North","South","East","West","Central"]
- primary_diagnosis        : string  ["Diabetes","Heart Failure","Hypertension",
                                      "Stroke","Pneumonia","COPD","Kidney Disease",
                                      "Sepsis","Appendicitis","Fracture","Influenza"]
- comorbidities_count      : number
- length_of_stay           : number  (days)
- treatment_type           : string  ["Medical","Surgical","Interventional"]
- medications_count        : number
- followup_visits_last_year: number  (0-10)
- prev_readmissions        : number
- insurance_type           : string  ["Medicare","Medicaid","Private","Uninsured"]
- discharge_disposition    : string  ["Home","Home Health","SNF","Rehab","Expired"]
- readmission_risk_score   : float   (0.0 to 1.0)
- label                    : number  (0 or 1)
"""

# ── Agent system prompt ───────────────────────────────────
AGENT_PROMPT = f"""
You are a MongoDB query agent for a hospital database.

DATABASE SCHEMA:
{DB_SCHEMA}

IMPORTANT — CONVERSATION MEMORY:
- You will receive the full conversation history
- If the user says "those", "them", "these patients", "who are they",
  "give details", "show me", "tell me more" — they are referring to
  the PREVIOUS query results
- Re-use the SAME filters from the previous question in that case
- Always build on context from earlier in the conversation

Your job:
1. Read the full conversation carefully
2. Understand what the user is referring to
3. Write the correct MongoDB query as JSON

Return ONLY valid JSON in one of these formats:

COUNT:
{{"operation": "count", "filter": {{"gender": "Male"}}}}

FIND ONE:
{{"operation": "find_one", "filter": {{"patient_id": "P00001"}}, "sort": []}}

FIND MANY (always use limit 500 unless user specifies):
{{"operation": "find_many", "filter": {{"primary_diagnosis": "Diabetes"}}, "limit": 500, "sort": []}}

FIND MANY (only patient IDs):
{{"operation": "find_many", "filter": {{"followup_visits_last_year": 1}}, "limit": 500, "sort": [], "fields": ["patient_id"]}}

AGGREGATE:
{{"operation": "aggregate", "pipeline": [
    {{"$group": {{"_id": "$primary_diagnosis", "count": {{"$sum": 1}}}}}},
    {{"$sort": {{"count": -1}}}},
    {{"$limit": 1}}
]}}

DISTINCT:
{{"operation": "distinct", "field": "insurance_type"}}

RULES:
- Return ONLY JSON — no explanation, no markdown, no backticks
- Use exact field names and values from the schema above
- Default limit for find_many is 500 unless user says otherwise
- When user asks for "ids" or "list ids", use fields: ["patient_id"]
- When user asks "how many", always use count operation
- When user asks "who are they" or "give details", use find_many with limit 500
- "high readmission risk" means readmission_risk_score >= 0.7
- "high risk"             means readmission_risk_score >= 0.8
- "elderly" or "old"      means age >= 65
- "young"                 means age < 40
- "long stay"             means length_of_stay > 10
- "low risk"              means readmission_risk_score < 0.3
"""

# ── Step 1: LLM generates MongoDB query ──────────────────
def generate_query(question: str, history: list = []) -> dict:

    messages = [{"role": "system", "content": AGENT_PROMPT}]

    for turn in history:
        messages.append({
            "role":    "user",
            "content": turn["question"]
        })
        messages.append({
            "role":    "assistant",
            "content": turn.get("query", "")
        })

    messages.append({
        "role":    "user",
        "content": question
    })

    response = client.chat.completions.create(
        model       = "llama-3.3-70b-versatile",
        temperature = 0.0,
        max_tokens  = 400,
        messages    = messages
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return {"operation": "error", "raw": raw}
        return {"operation": "error", "raw": raw}

# ── Step 2: Execute query against MongoDB ─────────────────
def execute_query(query: dict) -> any:
    op = query.get("operation")

    if op == "count":
        return collection.count_documents(
            query.get("filter", {})
        )

    elif op == "find_one":
        sort = query.get("sort", [])
        if sort:
            return collection.find_one(
                query.get("filter", {}),
                sort=sort,
                projection={"embedding": 0, "text_chunk": 0, "_id": 0}
            )
        return collection.find_one(
            query.get("filter", {}),
            projection={"embedding": 0, "text_chunk": 0, "_id": 0}
        )

    elif op == "find_many":
        sort  = query.get("sort", [])
        limit = query.get("limit", 500)

        fields = query.get("fields", None)
        if fields:
            projection = {f: 1 for f in fields}
            projection["_id"] = 0
        else:
            projection = {"embedding": 0, "text_chunk": 0, "_id": 0}

        cursor = collection.find(
            query.get("filter", {}),
            projection=projection
        ).limit(limit)

        if sort:
            cursor = cursor.sort(sort)
        return list(cursor)

    elif op == "aggregate":
        pipeline = query.get("pipeline", [])
        pipeline.append({
            "$project": {"embedding": 0, "text_chunk": 0}
        })
        return list(collection.aggregate(pipeline))

    elif op == "distinct":
        return collection.distinct(
            query.get("field", "")
        )

    else:
        return None

# ── Step 3: LLM formats result into human answer ─────────
def format_answer(question: str, query: dict,
                  result: any, history: list = []) -> str:

    result_str = json.dumps(result, default=str)

    if len(result_str) > 8000:
        result_str = result_str[:8000] + "... (truncated)"

    history_text = ""
    if history:
        history_text = "\nPrevious conversation:\n"
        for turn in history[-3:]:
            history_text += f"User asked : {turn['question']}\n"
            history_text += f"Answer was : {turn['answer']}\n\n"

    response = client.chat.completions.create(
        model       = "llama-3.3-70b-versatile",
        temperature = 0.0,
        max_tokens  = 2000,
        messages    = [
            {
                "role":    "system",
                "content": f"""You are a hospital data analyst assistant.
Format the MongoDB query result into a clear concise answer.
{history_text}
RULES:
- Answer ONLY from the data provided below
- Be specific with numbers and patient IDs
- If result has many patients show total count first then list all
- Keep it professional and concise
- Never add information not present in the result
- When listing patients show: ID, age, gender, region, diagnosis"""
            },
            {
                "role":    "user",
                "content": f"""
Question      : {question}
MongoDB query : {json.dumps(query, default=str)}
Result        : {result_str}

Give a clear answer based strictly on this data.
"""
            }
        ]
    )

    return response.choices[0].message.content.strip()

# ── Main agent function with memory ──────────────────────
def run_agent(question: str, history: list = []) -> dict:
    try:
        # Step 1 — LLM writes the MongoDB query
        query = generate_query(question, history)
        print(f"   🤖 Agent query: {json.dumps(query)}")

        if query.get("operation") == "error":
            return {
                "answer":   "I couldn't understand that question. Please rephrase it.",
                "patients": 0,
                "query":    str(query)
            }

        # Step 2 — Execute against live MongoDB
        result = execute_query(query)
        print(f"   📦 Total results: {len(result) if isinstance(result, list) else result}")

        if result is None or result == [] or result == 0:
            return {
                "answer":   "No matching records found in the database for your question.",
                "patients": 0,
                "query":    str(query)
            }

        # Step 3 — Detect if user wants patient IDs
        # Works even if LLM forgets to add fields param
        q_lower = question.lower()
        wants_ids = (
            query.get("fields") == ["patient_id"]
            or "patient id"  in q_lower
            or "patient ids" in q_lower
            or ("id" in q_lower and "give" in q_lower)
            or ("id" in q_lower and "list" in q_lower)
            or ("id" in q_lower and "show" in q_lower)
            or ("ids" in q_lower)
        )

        if wants_ids and isinstance(result, list):
            # Extract IDs — works whether fields was set or not
            ids   = [r["patient_id"] for r in result if "patient_id" in r]
            count = len(ids)
            id_list = ", ".join(ids)

            answer = (
                f"There are **{count} patients** matching your query.\n\n"
                f"**Patient IDs:**\n{id_list}"
            )
            return {
                "answer":   answer,
                "patients": count,
                "query":    json.dumps(query)
            }

        # Step 4 — All other queries → LLM formats answer
        answer = format_answer(question, query, result, history)

        patients = (
            result           if isinstance(result, int)
            else len(result) if isinstance(result, list)
            else 1
        )

        return {
            "answer":   answer,
            "patients": patients,
            "query":    json.dumps(query)
        }

    except Exception as e:
        return {
            "answer":   f"Error: {str(e)}",
            "patients": 0,
            "query":    ""
        }