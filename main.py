import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from groq import Groq

# --- ENV VARS ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- SIMPLE MEMORY (temporary) ---
memory = {}

# --- MAIN REPLY HANDLER ---
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id)
        user_text = update.message.text

        # create memory bucket
        if user_id not in memory:
            memory[user_id] = []

        # store user message
        memory[user_id].append({"role": "user", "content": user_text})

        # keep last 10 messages only
        memory[user_id] = memory[user_id][-10:]

        # AI call
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=memory[user_id]
        )

        answer = response.choices[0].message.content

        # store assistant reply
        memory[user_id].append({"role": "assistant", "content": answer})

        await update.message.reply_text(answer)

    except Exception as e:
        print("error:", e)
        await update.message.reply_text("bot alive, ai not working")

# --- BOT START ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("Bot running...")
    app.run_polling()

main()
