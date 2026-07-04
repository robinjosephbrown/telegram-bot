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

# --- SAFE GET ---
def safe(value):
    if value is None:
        return "unknown"
    return value

# --- REPLY ---
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

        # --- extract name ---
        if "my name is" in text:
            user["name"] = user_text.split("is")[-1].strip()

        # --- extract likes ---
        if "i like" in text:
            like = user_text.split("like")[-1].strip()
            if like:
                user["likes"].append(like)
                user["likes"] = user["likes"][-10:]

        # --- store chat ---
        user["chat"].append({"role": "user", "content": user_text})
        user["chat"] = user["chat"][-10:]

        # --- STRONG SYSTEM RULES ---
        system = {
            "role": "system",
            "content": f"""
You are a strict memory-based assistant.

RULES:
- Only use the user profile below.
- If something is unknown, say "I don't know".
- NEVER guess or invent facts.
- Do not halluc
