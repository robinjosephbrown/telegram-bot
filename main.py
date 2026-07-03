from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUR_CHAT_ID = 6807975624

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def on_start(app):
    await app.bot.send_message(
        chat_id=YOUR_CHAT_ID,
        text="I'm online. I'm watching."
    )
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"alive. chat_id = {chat_id}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.post_init = on_start

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("Bot running...")
    app.run_polling()

main()
