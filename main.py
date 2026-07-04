import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from groq import Groq

# =====================
# ENV
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =====================
# MEMORY
# =====================
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
    except:
        pass


memory = load_memory()


def safe(x):
    return x if x else "unknown"


# =====================
# BOT
# =====================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id)
        text = update.message.text
        lower = text.lower()

        # ---------------- INIT USER ----------------
        if user_id not in memory["users"]:
            memory["users"][user_id] = {
                "name": None,
                "likes": [],
                "goals": [],
                "chat": []
            }

        user = memory["users"][user_id]

        # ---------------- FACT EXTRACTION ----------------
        if "my name is" in lower:
            user["name"] = text.split("is")[-1].strip()

        if "
