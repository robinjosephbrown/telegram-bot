from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # OR paste token directly

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am alive")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, reply))

print("Bot running...")
app.run_polling()
