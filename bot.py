import telebot
import requests
import json
import os
import threading
from telebot import types
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.getenv("TOKEN", "")
MASTER_KEY = os.getenv("MASTER_KEY", "default123")
OWNER_ID = int(os.getenv("OWNER_ID", "453561961"))
OWNER_USERNAME = "@Kusainov10"
FREE_DAYS = 7

bot = telebot.TeleBot(TOKEN)

DB = TinyDB("users.json")
USERS_DB = DB.table("users")
LANG_DB = DB.table("languages")

WATCHLIST = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "NFLX", "AMD", "INTC"]
CRYPTO_LIST = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT"]

LANG = {
    "ru": {
        "name": "🇷🇺 Русский", "choose": "🌐 Выберите язык:",
        "lang_set": "Язык: Русский", "sub_expired": "⛔ Подписка истекла.",
        "welcome_trial": "👋 *Привет, {name}!*\n🎁 Пробный период: {days} дн.",
        "welcome_back": "👋 *С возвращением!*\n💳 Подписка: *{days}* дн.",
        "welcome_no_access": "👋 *Market Pulse*\n\nДоступ по подписке.\n📱 {owner}",
        "main_menu": "Главное меню",
        "btn_price": "📊 Цена", "btn_stocks": "📋 Акции",
        "btn_crypto": "🪙 Крипта", "btn_lang": "🌐 Язык",
        "btn_help": "ℹ️ Помощь", "btn_profile": "👤 Профиль",
        "btn_subscribe": "💳 Подписка",
    },
    "en": {
        "name": "🇬🇧 English", "choose": "🌐 Choose language:",
        "lang_set": "Language: English", "sub_expired": "⛔ Subscription expired.",
        "welcome_trial": "👋 *Hello, {name}!*\n🎁 Trial: {days} days.",
        "welcome_back": "👋 *Welcome back!*\n💳 Subscription: *{days}* days.",
        "welcome_no_access": "👋 *Market Pulse*\n\nSubscription access.\n📱 {owner}",
        "main_menu": "Main menu",
        "btn_price": "📊 Price", "btn_stocks": "📋 Stocks",
        "btn_crypto": "🪙 Crypto", "btn_lang": "🌐 Language",
        "btn_help": "ℹ️ Help", "btn_profile": "👤 Profile",
        "btn_subscribe": "💳 Subscribe",
    }
}

def get_user_lang(uid):
    User = Query()
    entry = LANG_DB.get(User.id == uid)
    return LANG.get(entry.get("lang"), LANG["ru"]) if entry else None

def set_user_lang(uid, code):
    User = Query()
    LANG_DB.upsert({"id": uid, "lang": code}, User.id == uid)

def get_lang(message):
    lang = get_user_lang(message.from_user.id)
    if lang: return lang
    return LANG["en"]

def lang_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    )
    return markup

def is_allowed(user_id):
    if user_id == OWNER_ID: return True
    User = Query()
    user = USERS_DB.get(User.id == user_id)
    if not user: return False
    return datetime.fromisoformat(user["expires"]) > datetime.now()

def register_user(user_id):
    User = Query()
    if not USERS_DB.get(User.id == user_id):
        USERS_DB.insert({"id": user_id, "expires": (datetime.now() + timedelta(days=FREE_DAYS)).isoformat()})
        return True
    return False

def days_left(user_id):
    User = Query()
    user = USERS_DB.get(User.id == user_id)
    if user:
        delta = datetime.fromisoformat(user["expires"]) - datetime.now()
        return max(0, delta.days)
    return 0

def get_price(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params={"range": "2d", "interval": "1d"})
    data = r.json()["chart"]["result"][0]
    prices = data["indicators"]["quote"][0]["close"]
    current = data["meta"]["regularMarketPrice"]
    prev = prices[-2] if len(prices) >= 2 and prices[-2] else current
    return {"price": current, "change": ((current - prev) / prev) * 100 if prev else 0}

def get_crypto_price(symbol):
    data = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}").json()
    current, prev = float(data["lastPrice"]), float(data["openPrice"])
    return {"price": current, "change": ((current - prev) / prev) * 100}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    uid = message.from_user.id
    args = message.text.split()
    is_invite = len(args) > 1 and args[1] == "invite"
    
    existing = get_user_lang(uid)
    if not existing:
        bot.send_message(uid, "🌐 Выберите язык / Choose language:", reply_markup=lang_menu())
        if is_invite: register_user(uid)
        return
    
    lang = existing
    if is_invite:
        is_new = register_user(uid)
    else:
        is_new = False
    
    if not is_allowed(uid):
        bot.send_message(uid, lang["welcome_no_access"].format(owner=OWNER_USERNAME), parse_mode="Markdown")
        return
    
    days = days_left(uid)
    if is_new and is_invite:
        text = lang["welcome_trial"].format(name=message.from_user.first_name, days=FREE_DAYS)
    else:
        text = lang["welcome_back"].format(name=message.from_user.first_name, days=days)
    
    bot.send_message(uid, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def main_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(lang["btn_price"]), types.KeyboardButton(lang["btn_stocks"]),
        types.KeyboardButton(lang["btn_crypto"]), types.KeyboardButton(lang["btn_lang"]),
        types.KeyboardButton(lang["btn_profile"]), types.KeyboardButton(lang["btn_subscribe"]),
        types.KeyboardButton(lang["btn_help"])
    )
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def callback_lang(call):
    uid = call.from_user.id
    code = call.data.replace("lang_", "")
    set_user_lang(uid, code)
    lang = LANG[code]
    bot.answer_callback_query(call.id, lang["lang_set"])
    bot.delete_message(uid, call.message.message_id)
    
    if is_allowed(uid):
        days = days_left(uid)
        text = lang["welcome_back"].format(name=call.from_user.first_name, days=days)
        bot.send_message(uid, text, parse_mode="Markdown", reply_markup=main_menu(lang))
    else:
        bot.send_message(uid, lang["welcome_no_access"].format(owner=OWNER_USERNAME), parse_mode="Markdown")

@bot.message_handler(commands=['price'])
def send_price(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    try:
        t = message.text.split()[1].upper()
        d = get_crypto_price(t) if t.endswith("USDT") else get_price(t)
        e = "📈" if d["change"] >= 0 else "📉"
        bot.send_message(message.chat.id, f"*{t}*\n💰 ${d['price']:.2f} {e} {d['change']:+.2f}%", parse_mode="Markdown", reply_markup=main_menu(lang))
    except:
        bot.reply_to(message, "❌")

@bot.message_handler(commands=['me'])
def cmd_me(message):
    if not is_allowed(message.from_user.id): return
    uid = message.from_user.id
    bot.send_message(uid, f"👤 ID: `{uid}`\nПодписка: *{days_left(uid)}* дн.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    uid = message.from_user.id
    lang = get_lang(message)
    
    if message.text == lang["btn_lang"]:
        bot.send_message(uid, lang["choose"], reply_markup=lang_menu())
        return
    
    if not is_allowed(uid):
        bot.reply_to(message, lang["sub_expired"])
        return
    
    if message.text == lang["btn_price"]:
        msg = bot.reply_to(message, "Тикер:", reply_markup=types.ForceReply(selective=True))
        bot.register_next_step_handler(msg, lambda m: process_ticker(m, lang))
    elif message.text == lang["btn_profile"]:
        bot.send_message(uid, f"👤 ID: `{uid}`\nПодписка: *{days_left(uid)}* дн.\nЯзык: {lang['name']}\nВладелец: {OWNER_USERNAME}", parse_mode="Markdown")
    elif message.text == lang["btn_subscribe"]:
        bot.send_message(uid, f"💳 Подписка: *{days_left(uid)}* дн.\n\nДля продления: {OWNER_USERNAME}", parse_mode="Markdown")
    elif message.text == lang["btn_help"]:
        bot.send_message(uid, "ℹ️ Market Pulse\n\n/price ТИКЕР — цена\n/me — профиль", reply_markup=main_menu(lang))
    else:
        try:
            t = message.text.upper()
            d = get_crypto_price(t) if t.endswith("USDT") else get_price(t)
            e = "📈" if d["change"] >= 0 else "📉"
            bot.send_message(uid, f"*{t}*\n💰 ${d['price']:.2f} {e} {d['change']:+.2f}%", parse_mode="Markdown", reply_markup=main_menu(lang))
        except:
            bot.reply_to(message, "Меню ↓", reply_markup=main_menu(lang))

def process_ticker(message, lang):
    try:
        t = message.text.upper()
        d = get_crypto_price(t) if t.endswith("USDT") else get_price(t)
        e = "📈" if d["change"] >= 0 else "📉"
        bot.send_message(message.chat.id, f"*{t}*\n💰 ${d['price']:.2f} {e} {d['change']:+.2f}%", parse_mode="Markdown", reply_markup=main_menu(lang))
    except:
        bot.reply_to(message, "❌", reply_markup=main_menu(lang))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    server = HTTPServer(("0.0.0.0", 10000), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

if __name__ == '__main__':
    print("Market Pulse запущен")
    bot.infinity_polling()
