import telebot
from telebot import types
from dotenv import load_dotenv
import os
import requests

# load bot token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API = os.getenv("WEATHER_API")

bot = telebot.TeleBot(BOT_TOKEN)

# handling /start command
@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Get currency exchange', callback_data='currency'))
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name}!\nWhat country would you like to explore?', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_country(message):
    country = message.text.strip().lower()
    res = requests.get(f'https://restcountries.com/v3.1/name/{country}')
    print(res)
    if res.status_code == 200:
        data_list = res.json()
        data = data_list[0]
        name = data['name']['common']
        capital = data.get('capital', ['N/A'])[0]
        region = data['region']
        population = data['population']
        flag = data.get('flags', {}).get('emoji', '')
        maps = data['maps']['googleMaps']
        currency = ', '.join(data.get('currencies', {}).keys())
        languages = ', '.join(data.get('languages', {}).values())
        temperature = get_temperature(capital)

        text = (
            f'{flag} *{name}*\n'
            f'Capital: {capital}\n'
            f'Region: {region}\n'
            f'Population: {population}\n'
            f'Currency: {currency}\n'
            f'Language: {languages}\n'
            f'Temperature: {temperature} °C\n'
            f'Map: {maps}'
        )
        bot.reply_to(message, text, parse_mode='Markdown')
    else:
        bot.reply_to(message, 'Country not found.')

def get_temperature(city):
    res = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric')
    if res.status_code == 200:
        temp_data = res.json()
        temperature = temp_data["main"]["temp"]
        return temperature
    else:
        return "Sorry, temperature info is currently unavailable"

def get_currency():
    pass

bot.polling(non_stop=True)