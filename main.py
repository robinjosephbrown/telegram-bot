from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = "8826394576:AAFZk1x6cKXHajrIRHdxWIqkjj8EvJFdgD8"
PORT = int(os.environ.get("PORT", "10000"))

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am alive")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, reply))

print("Bot running (webhook mode ready)")
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=BOT_TOKEN,
    webhook_url=f"https://telegram-bot-iibh.onrender.com/{BOT_TOKEN}"
)
