import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from groq import Groq

# --- ENV VARS ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- MAIN REPLY HANDLER ---
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": user_text}
            ]
        )

        answer = response.choices[0].message.content
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
