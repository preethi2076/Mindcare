from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from memory import store_memory, retrieve_memory, get_user_memories
import openai
import os

openai.api_key = os.getenv("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")  # set env variable

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MENTAL_KEYWORDS = [
    "stress", "anxiety", "anxious", "depressed", "sad",
    "exam", "pressure", "fear", "panic", "lonely", "mental"
]

def is_mental_health(text: str):
    t = text.lower()
    return any(k in t for k in MENTAL_KEYWORDS)

def llm_reply(user_text, memories, mood):
    context = "\n".join([m["text"] for m in memories])

    prompt = f"""
You are a supportive mental health assistant.
Do NOT give medical diagnosis.
Be empathetic and short.

User mood: {mood}
Past memories:
{context}

User says: {user_text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )

    return response.choices[0].message.content.strip()
@app.post("/login")
def login(username: str):
    if not username:
        return {"error": "Username required"}

    return {
        "session_id": username.strip().lower()
    }

@app.post("/chat")
def chat(text: str, mood: str, session: str):

    try:
        print("CHAT INPUT:", text, mood, session)

        store_memory(text, mood, session)
        print("MEMORY STORED")

        memories = retrieve_memory(text, session)
        print("MEMORY RETRIEVED:", memories)

        bot_reply = f"I hear you. Feeling {mood} can be difficult."

        return {
            "response": bot_reply,
            "retrieved_memory": memories
        }

    except Exception as e:
        print("🔥 SERVER ERROR:", e)
        return {
            "response": "Sorry, something went wrong on the server.",
            "retrieved_memory": []
        }

ADMIN_KEY = "admin123"  # change if you want

@app.get("/admin/memory")
def view_memory(user: str, key: str):
    if key != ADMIN_KEY:
        return {"error": "Unauthorized"}

    memories = get_user_memories(user)
    return {
        "user": user,
        "memory_count": len(memories),
        "memories": memories
    }
