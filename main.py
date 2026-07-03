from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

app_web = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am alive")

bot = ApplicationBuilder().token(BOT_TOKEN).build()
bot.add_handler(MessageHandler(filters.TEXT, reply))

# Web server for Render
@app_web.route("/")
def home():
    return "Bot is alive"

print("Bot running")

bot.run_polling()
