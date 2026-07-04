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
    return x if x is not None else "unknown"

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id)
        text = update.message.text

        if user_id not in memory["users"]:
            memory["users"][user_id] = {
                "name": None,
                "likes": [],
                "chat": []
            }

        user = memory["users"][user_id]

        lower = text.lower()

        if "my name is" in lower:
            user["name"] = text.split("is")[-1].strip()

        if "i like" in lower:
            like = text.split("like")[-1].strip()
            if like:
                user["likes"].append(like)
                user["likes"] = user["likes"][-10:]

        user["chat"].append({"role": "user", "content": text})
        user["chat"] = user["chat"][-10:]

        system = {
            "role": "system",
            "content": (
                "You are a strict assistant.\n"
                "Do not guess missing info.\n"
                "If unknown say 'I don't know'.\n\n"
                f"Name: {safe(user['name'])}\n"
                f"Likes: {safe(user['likes'])}\n"
            )
        }

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[system] + user["chat"]
        )

        answer = response.choices[0].message.content

        user["chat"].append({"role": "assistant", "content": answer})

        save_memory(memory)

        await update.message.reply_text(answer)

    except Exception as e:
        print("error:", e)
        await update.message.reply_text("bot alive, ai not working")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("Bot running...")
    app.run_polling()

main()
