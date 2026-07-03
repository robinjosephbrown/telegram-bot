from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import os

BOT_TOKEN = "8826394576:AAFZk1x6cKXHajrIRHdxWIqkjj8EvJFdgD8"

def reply(update: Update, context: CallbackContext):
    update.message.reply_text("I am alive")

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text, reply))

print("Bot running...")
updater.start_polling()
updater.idle()
