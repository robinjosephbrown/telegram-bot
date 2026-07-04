import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id)
        text = update.message.text
        lower = text.lower()

        if user_id not in memory["users"]:
            memory["users"][user_id] = {
                "name": None,
                "likes": [],
                "goals": [],
                "chat": []
            }

        user = memory["users"][user_id]

        # memory extraction
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

        # direct answers
        if lower in ["what is my name", "what's my name"]:
            await update.message.reply_text(user["name"] or "I don't know yet.")
            return

        if lower in ["what is your name", "what's your name"]:
            await update.message.reply_text("I am Oblivion.")
            return

        if lower in ["what do i like", "what are my likes"]:
            await update.message.reply_text(", ".join(user["likes"]) or "I don't know yet.")
            return

        # chat history
        user["chat"].append({"role": "user", "content": text})
        user["chat"] = user["chat"][-12:]

        system_text = (
            "You are Oblivion, a companion AI.\n"
            "You are NOT allowed to change user facts.\n"
            "Be natural and conversational.\n\n"
            f"User name: {safe(user['name'])}\n"
            f"User likes: {safe(user['likes'])}\n"
            f"User goals: {safe(user['goals'])}\n"
        )

        messages = [{"role": "system", "content": system_text}] + user["chat"]

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        answer = response.choices[0].message.content

        user["chat"].append({"role": "assistant", "content": answer})

        save_memory(memory)

        await update.message.reply_text(answer)

    except Exception as e:
        print("error:", e)
        await update.message.reply_text("bot alive, ai not working")
