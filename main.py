from telebot import TeleBot
from config import TELEGRAM_TOKEN
bot = TeleBot(TELEGRAM_TOKEN)

# 🔥 Bu satırı ekle
bot.remove_webhook()
import telebot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from helpers import analyze_coin
import time

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    symbol = message.text.strip().upper()
    result = analyze_coin(symbol)
    bot.send_message(TELEGRAM_CHAT_ID, result)

print("Bot is polling...")
bot.polling()
