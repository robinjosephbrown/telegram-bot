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
    with open(MEM_FILE, "w") as f:
        json.dump(data, f)

memory = load_memory()

# --- REPLY HANDLER ---
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

        # --- extract simple facts ---
        text = user_text.lower()

        if "my name is" in text:
            user["name"] = user_text.split("is")[-1].strip()

        if "i like" in text:
            like = user_text.split("like")[-1].strip()
            user["likes"].append(like)
            user["likes"] = user["likes"][-10:]

        # --- store chat ---
        user["chat"].append({"role": "user", "content": user_text})
        user["chat"] = user["chat"][-10:]

        # --- system memory (truth layer) ---
        system = {
            "role": "system",
            "content": f"""
You are a helpful assistant.

User info:
- Name: {user['name']}
- Likes: {user['likes']}

Use this info consistently. Do not guess missing facts.
"""
        }

        messages = [system] + user["chat"]

        # --- AI CALL ---
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        answer = response.choices[0].message.content

        # --- store assistant reply ---
        user["chat"].append({"role": "assistant", "content": answer})

        # --- save memory ---
        save_memory(memory)

        await update.message.reply_text(answer)

    except Exception as e:
        print("error:", e)
        await update.message.reply_text("bot alive, ai not working")

# --- START BOT ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("Bot running...")
    app.run_polling()

main()
