import telebot
from telebot import types
from dotenv import load_dotenv
import os
import requests
from currency_converter import CurrencyConverter

# load bot token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API = os.getenv("WEATHER_API")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# CLIENT_ID = os.getenv("CLIENT_ID")

bot = telebot.TeleBot(BOT_TOKEN)
currency_converter = CurrencyConverter()

# handling /start command
@bot.message_handler(commands=['start'])
def main(message):
    # markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton('Get currency exchange', callback_data='currency'))
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name}!\nWhat country would you like to explore?')

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

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Get currency exchange', callback_data='currency'))
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
        bot.reply_to(message, text, parse_mode='Markdown', reply_markup=markup)
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

# def get_places():
#
#     token_res = requests.post(
#         "https://test.api.amadeus.com/v1/security/oauth2/token",
#         data={
#             "grant_type": "client_credentials",
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET
#         }
#     )
#     token_res.raise_for_status()
#     access_token = token_res.json()["access_token"]
#
#     # Запрос к Tours & Activities
#     latitude = 41.397158  # пример — можно заменить на координаты города
#     longitude = 2.160873
#     radius = 5000  # радиус в метрах
#
#     url = "https://test.api.amadeus.com/v1/shopping/activities"
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     params = {
#         "latitude": latitude,
#         "longitude": longitude,
#         "radius": radius
#     }
#     res = requests.get(url, headers=headers, params=params)
#     res.raise_for_status()  # добавим проверку на ошибки
#     data = res.json()
#     for activity in data.get("data", [])[:3]:
#         name = activity.get("name")
#         price_info = activity.get("price", {})
#         amount = price_info.get("amount")
#         currency = price_info.get("currency")
#         print(f"Name: {name}, Price: {amount} {currency}")

@bot.callback_query_handler(func=lambda call: call.data == 'currency')
def get_currency(call):
    bot.send_message(call.message.chat.id, 'Enter amount, please.')

bot.polling(non_stop=True)