import telebot
from telebot import types
from dotenv import load_dotenv
import os

# load bot token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# handling /start command