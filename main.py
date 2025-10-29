import telebot
from telebot import types
from dotenv import load_dotenv
import os

# load bot token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# handling /start command
@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Get currency exchange', callback_data='currency'))
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name}!\nWhat country would you like to explore?', reply_markup=markup)

def get_currency():
    pass

bot.polling(non_stop=True)