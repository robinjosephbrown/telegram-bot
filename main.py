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
# MEMORY FILE
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
# MAIN BOT LOGIC
# =====================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id)
        text = update.message.text
        lower = text.lower()

        # ---------------------
        # INIT USER PROFILE
        # ---------------------
        if user_id not in memory["users"]:
            memory["users"][user_id] = {
                "name": None,
                "likes": [],
                "goals": [],
                "facts": {},
                "summary": "",
                "chat": []
            }

        user = memory["users"][user_id]

        # ---------------------
        # SIMPLE MEMORY EXTRACTION
        # ---------------------
        if "my name is" in lower:
            user["name"] = text.split("is")[-1].strip()

        if "i like" in lower:
            like = text.split("like")[-1].strip()
            if like:
                user["likes"].append(like)
                user["likes"] = user["likes"][-10:]

        if "my goal is" in lower:
            goal = text.split("is")[-1].strip()
            if goal:
                user["goals"].append(goal)
                user["goals"] = user["goals"][-10:]

        # ---------------------
        # DIRECT FACT ANSWERS (prevents AI confusion)
        # ---------------------
        if lower in ["what is my name", "what's my name"]:
            await update.message.reply_text(user["name"] or "I don't know your name yet.")
            return

        if lower in ["what do i like", "what are my likes"]:
            await update.message.reply_text(", ".join(user["likes"]) or "I don't know what you like yet.")
            return

        if lower in ["what is your name", "what's your name"]:
            await update.message.reply_text("I am Oblivion.")
            return

        # ---------------------
        # STORE CHAT
        # ---------------------
        user["chat"].append({"role": "user", "content": text})
        user["chat"] = user["chat"][-12:]

        # ---------------------
        # SYSTEM PROMPT (ALIVE CORE)
        # ---------------------
        system = {
            "role": "system",
            "content": f"""
You are Oblivion — a persistent AI companion.

You are NOT a tool.
