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

user_amounts = {}
user_states = {}

# handling /start command
@bot.message_handler(commands=['start'])
def main(message):
    user_states[message.chat.id] = None
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Get currency exchange', callback_data='currency'))
    markup.add(types.InlineKeyboardButton('Get country information', callback_data='country'))
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name}!\nChoose your operation.', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'country')
def country(call):
    user_states[call.message.chat.id] = 'awaiting_country'
    bot.send_message(call.message.chat.id,'What country would you like to explore?')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    state = user_states.get(message.chat.id)
    if state == 'awaiting_amount':
        summa(message)
    elif state == 'awaiting_country':
        get_country(message)
    elif state == 'awaiting_currency_pair':
        user_currency(message)
    else:
        bot.send_message(message.chat.id, 'Please select an operation first (/start).')

def get_country(message):
    country_title = message.text.strip().lower()
    res = requests.get(f'https://restcountries.com/v3.1/name/{country_title}')
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

def summa(message):
    try:
        user_amounts[message.chat.id] = float(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format, please enter a number.')
        bot.register_next_step_handler(message, summa)
        return

    if user_amounts[message.chat.id] > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD to EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR to USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('USD to GBP', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Other', callback_data='other')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Choose currency', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Amount must be greater than 0.')
        bot.register_next_step_handler(message, summa)
        return

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
    user_states[call.message.chat.id] = 'awaiting_amount'
    msg = bot.send_message(call.message.chat.id, 'Enter amount, please.')
    bot.register_next_step_handler(msg, summa)

@bot.callback_query_handler(func=lambda call: call.data in ['usd/eur', 'eur/usd', 'usd/gbp', 'other'])
def exchange(call):
    # user_states[call.message.chat.id] = 'awaiting_currency_pair'
    if call.data != 'other':
        amount = user_amounts.get(call.message.chat.id, 0)
        values = call.data.upper().split('/')
        try:
            res = round(currency_converter.convert(amount, values[0], values[1]), 2)
            text = (
                f'Result: {res}.\n'
                f'You can re-enter different amount.'
            )
        except Exception:
            text = 'Conversion failed. Try again.'
        bot.send_message(call.message.chat.id, text)
        user_states[call.message.chat.id] = None
        # bot.register_next_step_handler(call.message, summa)
    else:
        user_states[call.message.chat.id] = 'awaiting_currency_pair'
        bot.send_message(call.message.chat.id, 'Enter your currency pair separated by a slash')
        # bot.register_next_step_handler(call.message, user_currency)

def user_currency(message):
    try:
        values = message.text.upper().split('/')
        amount = user_amounts.get(message.chat.id, 0)
        res = round(currency_converter.convert(amount, values[0], values[1]), 2)
        text = (
            f'Result: {res}.\n'
            f'You can re-enter different amount.'
        )
        bot.send_message(message.chat.id, text)
        # bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, 'Conversion failed. Try again.')
        # bot.register_next_step_handler(message, summa)
        user_states[message.chat.id] = None

bot.polling(non_stop=True)