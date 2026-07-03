from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# CHANGE THIS to your Telegram user ID later
YOUR_CHAT_ID = 123456789

async def send_update(app):
    await app.bot.send_message(
        chat_id=YOUR_CHAT_ID,
        text="I checked the world. Everything is running."
    )

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am alive")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT, reply))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_update, "interval", seconds=60, args=[app])
    scheduler.start()

    print("Bot running...")
    app.run_polling()

main()
