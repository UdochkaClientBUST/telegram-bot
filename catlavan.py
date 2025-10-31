import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests

TOKEN = "7154288748:AAH_DjxqlB-Z8suCdyy6kig1TrmJIG0UV4Y"
WEATHER_API = "3de1ca6942ce022c87b532269688a39f"

bot = telebot.TeleBot(TOKEN)

user_lang = {}

def main_menu(lang):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    if lang == "uz":
        kb.add(KeyboardButton("🌤 Ob-havo"), KeyboardButton("💱 Kurs"))
        kb.add(KeyboardButton("🔔 Obuna"))
    elif lang == "ru":
        kb.add(KeyboardButton("🌤 Погода"), KeyboardButton("💱 Курсы"))
        kb.add(KeyboardButton("🔔 Подписка"))
    else:
        kb.add(KeyboardButton("🌤 Weather"), KeyboardButton("💱 Rates"))
        kb.add(KeyboardButton("🔔 Subscribe"))

    return kb


@bot.message_handler(commands=['start'])
def start(message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🇺🇿 Uzbek"), KeyboardButton("🇷🇺 Русский"))

    bot.send_message(
        message.chat.id,
        "Виберите язык / Select language / Tilni tanlang:",
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: m.text in ["🇺🇿 Uzbek", "🇷🇺 Русский"])
def set_lang(message):
    lang = "uz" if "Uzbek" in message.text else "ru"
    user_lang[message.chat.id] = lang

    if lang == "uz":
        bot.send_message(message.chat.id, "👋 Salom! Amal tanlang:", reply_markup=main_menu(lang))
    else:
        bot.send_message(message.chat.id, "👋 Привет! Выберите действие:", reply_markup=main_menu(lang))


def get_weather(city="Tashkent", lang="uz"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric&lang={lang}"
    res = requests.get(url).json()

    if "main" not in res:
        return "⚠️ Ob-havo ma'lumoti mavjud emas"

    temp = res["main"]["temp"]
    description = res["weather"][0]["description"]
    return f"🌥 {description.capitalize()} | {city}: {temp:.1f}°C"


def get_currency_rates():
    try:
        r = requests.get("https://cbu.uz/ru/arkhiv-kursov-valyut/json/").json()

        usd = next(x for x in r if x["Ccy"] == "USD")["Rate"]
        eur = next(x for x in r if x["Ccy"] == "EUR")["Rate"]
        rub = next(x for x in r if x["Ccy"] == "RUB")["Rate"]

        return (
            f"💵 USD: {usd} UZS\n"
            f"💶 EUR: {eur} UZS\n"
            f"🇷🇺 RUB: {rub} UZS"
        )
    except:
        return "⚠️ NBU dan valyuta olishda xatolik"



@bot.message_handler(func=lambda m: True)
def handler(message):
    lang = user_lang.get(message.chat.id, "uz")
    txt = message.text

    # WEATHER
    if txt in ["🌤 Ob-havo", "🌤 Погода", "🌤 Weather"]:
        bot.send_message(message.chat.id, get_weather(lang=lang))
        return

    # CURRENCY
    if txt in ["💱 Kurs", "💱 Курсы", "💱 Rates"]:
        bot.send_message(message.chat.id, get_currency_rates())
        return

    # SUBSCRIBE
    if txt in ['🔔 Obuna', '🔔 Подписка', '🔔 Subscribe']:
        bot.send_message(message.chat.id, text="✅ Siz obuna bo'ldingiz!")
        return
if __name__ == "__main__":
    print("✅ Bot ishga tushdi...")
    bot.polling(non_stop=True)
