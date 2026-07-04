import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from groq import Groq

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO)

# ---------- ENV ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_API_KEY:
    raise Exception("Missing BOT_TOKEN or GROQ_API_KEY in environment")

client = Groq(api_key=GROQ_API_KEY)

# ---------- MEMORY ----------
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


def safe(v):
    return v if v else "unknown"


# ---------- CORE BOT ----------
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return

        user_id = str(update.effective_chat.id)
        text = update.message.text.strip()
        lower = text.lower()

        # init user
        if user_id not in memory["users"]:
            memory["users"][user_id] = {
                "name": None,
                "likes": [],
                "chat": []
            }

        user = memory["users"][user_id]

        # ---------- SIMPLE MEMORY EXTRACTION ----------
        if "my name is" in lower:
            user["name"] = text.split("is")[-1].strip()

        if "i like" in lower:
            like = text.split("like")[-1].strip()
            if like:
                user["likes"].append(like)
                user["likes"] = user["likes"][-10:]

        # ---------- SHORTCUT ANSWERS ----------
        if lower in ["what is my name", "what's my name"]:
            await update.message.reply_text(user["name"] or "I don't know yet.")
            return

        if lower in ["what do i like", "what are my likes"]:
            await update.message.reply_text(", ".join(user["likes"]) or "I don't know yet.")
            return

        # ---------- CHAT HISTORY ----------
        user["chat"].append({"role": "user", "content": text})
        user["chat"] = user["chat"][-12:]

        system = {
            "role": "system",
            "content": (
                "You are Oblivion, a friendly AI companion.\n"
                "Be natural, slightly playful, but accurate.\n"
                "Never overwrite user memory yourself.\n\n"
                f"Name: {safe(user['name'])}\n"
                f"Likes: {safe(user['likes'])}\n"
            )
        }

        messages = [system] + user["chat"]

        # ---------- GROQ CALL ----------
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        answer = response.choices[0].message.content

        user["chat"].append({"role": "assistant", "content": answer})

        save_memory(memory)

        await update.message.reply_text(answer)

    except Exception as e:
        print("BOT ERROR:", e)
        await update.message.reply_text("bot alive, ai unstable")


# ---------- START ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("OBLIVION ONLINE")
    app.run_polling()


if __name__ == "__main__":
    main()
