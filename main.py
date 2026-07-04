import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from groq import Groq

# --- ENV ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- MEMORY FILE ---
MEM_FILE = "memory.json"

def load_memory():
    try:
        with open(MEM_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}}

def save_memory(data):
    try:
        with open(MEM_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("save error:", e)

memory = load_memory()

def safe(value):
    if value is None:
        return "unknown"
    return value

# --- MAIN HANDLER ---
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id)
        user_text = update.message.text

        # init user memory
        if user_id not in memory["users"]:
            memory["users"][user_id] = {
                "name": None,
                "likes": [],
                "chat": []
            }

        user = memory["users"][user_id]

        text = user_text.lower()

        # --- extract simple facts ---
        if "my name is" in text:
            user["name"] = user_text.split("is")[-1].strip()

        if "i like" in text:
            like = user_text.split("like")[-1].strip()
            if like:
                user["likes"].append(like)
                user["likes"] = user["likes"][-10:]

        # --- store chat ---
        user["chat"].append({"role": "user", "content": user_text})
        user["chat"] = user["chat"][-10:]

        # --- SYSTEM PROMPT (SAFE) ---
        system = {
            "role": "system",
            "content": (
                "You are a strict assistant with memory.\n"
                "RULES:\n"
                "- Use ONLY provided user info.\n"
                "- Do NOT guess missing data.\n"
                "- If unknown, say 'I don't know'.\n"
                "\n"
                "USER PROFILE:\n"
                f"- Name: {safe(user['name'])}\n"
                f"- Likes: {safe(user['likes'])}\n"
            )
        }

        messages = [system] + user["chat"]

        # --- AI CALL ---
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        answer = response.choices[0].message.content

        # --- store assistant reply ---
        user["chat"].append({"role": "
