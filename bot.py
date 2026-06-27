import telebot
import requests
import json
import os
import threading
from telebot import apihelper, types
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.getenv("TOKEN", "")
MASTER_KEY = os.getenv("MASTER_KEY", "default123")
OWNER_ID = int(os.getenv("OWNER_ID", "453561961"))
OWNER_USERNAME = "@Kusainov10"
CARD_NUMBER = "2200 7001 5852 1475"
USDT_ADDRESS = "0x0AC33B189ef7CAa33a8e4655A19318ACADD057a5"
TON_ADDRESS = "UQBpNSeDQ79erS--C-2L3YcMxCMPdB6kp2--gS-hwRM-l8B7"
FREE_DAYS = 7

bot = telebot.TeleBot(TOKEN)

DB = TinyDB("users.json")
USERS_DB = DB.table("users")
LANG_DB = DB.table("languages")

WATCHLIST = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "NFLX", "AMD", "INTC"]
CRYPTO_LIST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "DOTUSDT"]

US_STOCKS = {"🍎 Apple": "AAPL", "🚗 Tesla": "TSLA", "🔍 Google": "GOOGL", "📦 Amazon": "AMZN", "🪟 Microsoft": "MSFT", "🎮 NVIDIA": "NVDA", "👤 Meta": "META", "🎬 Netflix": "NFLX", "💻 AMD": "AMD", "🔷 Intel": "INTC", "🏦 JPMorgan": "JPM", "💊 Pfizer": "PFE", "🛢 Exxon": "XOM", "📱 Adobe": "ADBE", "☁️ Salesforce": "CRM"}
RU_STOCKS = {"🏦 Сбер": "SBER.ME", "⛽️ Газпром": "GAZP.ME", "🛢 Лукойл": "LKOH.ME", "🔍 Яндекс": "YNDX.ME", "💰 ВТБ": "VTBR.ME", "🥇 Норникель": "GMKN.ME", "🛢 Роснефть": "ROSN.ME", "🏪 Магнит": "MGNT.ME", "⛽️ Сургутнефтегаз": "SNGS.ME", "⚡️ Новатэк": "NVTK.ME"}
CN_STOCKS = {"🛒 Alibaba": "BABA", "🔍 Baidu": "BIDU", "🚗 NIO": "NIO", "📦 JD.com": "JD", "🛍 Pinduoduo": "PDD", "🎮 Tencent": "TCEHY"}
EU_STOCKS = {"👜 LVMH": "LVMUY", "💻 ASML": "ASML", "📊 SAP": "SAP", "⚙️ Siemens": "SIEGY", "🚗 BMW": "BMWYY", "✈️ Airbus": "EADSY", "🛡 Allianz": "ALIZF"}
TOP_CRYPTO = {"₿ Bitcoin": "BTCUSDT", "♦️ Ethereum": "ETHUSDT", "💎 Solana": "SOLUSDT", "🟠 BNB": "BNBUSDT", "🔷 XRP": "XRPUSDT", "🐶 Dogecoin": "DOGEUSDT"}
INDICES = {"🇺🇸 S&P 500": "SPY", "📊 NASDAQ": "QQQ", "🏛 Dow Jones": "DIA", "🇷🇺 MOEX": "IMOEX.ME"}

LANG = {
    "ru": {
        "name": "🇷🇺 Русский", "choose": "🌐 Выберите язык:",
        "lang_set": "Язык: Русский", "sub_expired": "⛔ Подписка истекла.",
        "wrong_key": "⛔ Неверный ключ.",
        "welcome_no_access": "👋 *Market Pulse*\n\nДоступ по подписке.\n📱 {owner}",
        "welcome_trial": "👋 *Привет, {name}!*\n🎁 Пробный период: {days} дн.",
        "welcome_back": "👋 *С возвращением, {name}!*\n💳 Подписка: *{days}* дн.\nЯзык: {lang_name}",
        "profile": "👤 ID: `{uid}`\nПодписка: *{days}* дн.\nЯзык: {lang_name}\nВладелец: {owner}",
        "price": "*{name}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 {ticker} на ${target:.2f} установлен!",
        "no_alerts": "🔔 Нет алертов.", "alerts_list": "🔔 *Алерты:*\n\n",
        "del_alert": "✅ {ticker} удалён",
        "stock_list": "📋 *Акции:*\n\n", "crypto_list": "🪙 *Крипта:*\n\n",
        "gainers": "🚀 *Рост:*\n\n", "losers": "📉 *Падение:*\n\n",
        "potential": "🔮 *Потенциал:*\n\n", "crypto_potential": "🔮 *Крипто потенциал:*\n\n",
        "news": "📰 *Новости:*\n\n", "no_news": "😴 Нет движений.",
        "no_candidates": "🔮 Нет кандидатов.",
        "help": "ℹ️ Market Pulse\n\n📊 Цена | 🪙 Крипта | 📈 RSI | 📉 График\n🔔 Алерты | 👤 Профиль | 🌐 Язык | 💳 Подписка",
        "enter_ticker": "Введи тикер:", "wrong_ticker": "❌ Неверный тикер",
        "use_buttons": "Используй меню.", "main_menu": "Главное меню",
        "crypto_menu": "🪙 Крипта", "searching_news": "📰 Ищу новости...",
        "backup_ok": "✅ Бекап создан.", "backup_fail": "❌ Ошибка.",
        "log_empty": "Лог пуст.", "no_users": "Нет пользователей.",
        "activated": "✅ {uid} активирован на {days} дн.",
        "notify_activated": "✅ Подписка продлена на {days} дней!",
        "users_list": "👥 *Пользователи:*\n\n",
        "subscription_info": "💳 *Подписка Market Pulse*\n\nОсталось: *{days}* дн.\n\nВыберите способ оплаты:",
        "market_summary": "📊 *Сводка рынка*\n\n",
        "hype_of_day": "🚀 *Хайп дня*\n\n",
        "signal_of_day": "🎯 *Сигнал дня*\n\n",
        "top_market_title": "🔥 *Топ рынка*\n\nВыберите раздел:",
        "btn_top_market": "🔥 Топ рынка",
        "btn_market_summary": "📊 Сводка рынка",
        "btn_hype_day": "🚀 Хайп дня",
        "btn_signal_day": "🎯 Сигнал дня",
        "btn_us_stocks": "🇺🇸 Акции США",
        "btn_ru_stocks": "🇷🇺 Акции РФ",
        "btn_cn_stocks": "🇨🇳 Акции Китая",
        "btn_eu_stocks": "🇪🇺 Акции Европы",
        "btn_crypto_top": "🪙 Крипто-топ",
        "btn_price": "📊 Цена", "btn_stocks": "📋 Акции",
        "btn_gainers": "🚀 Рост", "btn_losers": "📉 Падение",
        "btn_potential": "🔮 Потенциал", "btn_news": "📰 Новости",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 График",
        "btn_crypto": "🪙 Крипта", "btn_alerts": "🔔 Алерты",
        "btn_profile": "👤 Профиль", "btn_subscribe": "💳 Подписка",
        "btn_help": "ℹ️ Помощь", "btn_lang": "🌐 Язык",
        "btn_crypto_price": "🪙 Курс", "btn_crypto_list": "📋 Список",
        "btn_crypto_potential": "🔮 Потенциал", "btn_back": "🔙 Назад",
        "btn_tariff_30": "📅 30 дн. — 299₽",
        "btn_tariff_90": "📅 90 дн. — 699₽",
        "btn_tariff_365": "📅 365 дн. — 1999₽",
        "btn_card_pay": "💳 Банковская карта (РФ)",
        "btn_crypto_pay": "🪙 Криптовалюта (USDT)",
        "btn_ton_pay": "💎 Telegram Wallet (TON)",
        "btn_back_sub": "🔙 Назад",
        "crypto_tariff_30": "🪙 30 дн. — 10 USDT",
        "crypto_tariff_90": "🪙 90 дн. — 25 USDT",
        "crypto_tariff_365": "🪙 365 дн. — 70 USDT",
        "ton_tariff_30": "💎 30 дн. — 10 TON",
        "ton_tariff_90": "💎 90 дн. — 25 TON",
        "ton_tariff_365": "💎 365 дн. — 70 TON",
        "tariff_30_card": "📅 *30 дней — 299₽*\n\n💳 Карта: `{card}`\n\n⚠️ *Инструкция:*\n1. Переведите 299₽ на карту\n2. Комментарий: *«Market Pulse 30 дней»*\n3. Отправьте скриншот и ваш ID → {owner}\n\nВы получите чек от самозанятого.",
        "tariff_90_card": "📅 *90 дней — 699₽*\n\n💳 Карта: `{card}`\n\n⚠️ *Инструкция:*\n1. Переведите 699₽ на карту\n2. Комментарий: *«Market Pulse 90 дней»*\n3. Отправьте скриншот и ваш ID → {owner}\n\nВы получите чек от самозанятого.",
        "tariff_365_card": "📅 *365 дней — 1999₽*\n\n💳 Карта: `{card}`\n\n⚠️ *Инструкция:*\n1. Переведите 1999₽ на карту\n2. Комментарий: *«Market Pulse 365 дней»*\n3. Отправьте скриншот и ваш ID → {owner}\n\nВы получите чек от самозанятого.",
        "tariff_30_usdt": "🪙 *30 дней — 10 USDT*\n\n📤 Адрес USDT (ERC-20):\n`{usdt}`\n\n⚠️ *Инструкция:*\n1. Отправьте ровно 10 USDT\n2. Сеть: Ethereum (ERC-20)\n3. Отправьте скриншот и ваш ID → {owner}",
        "tariff_90_usdt": "🪙 *90 дней — 25 USDT*\n\n📤 Адрес USDT (ERC-20):\n`{usdt}`\n\n⚠️ *Инструкция:*\n1. Отправьте ровно 25 USDT\n2. Сеть: Ethereum (ERC-20)\n3. Отправьте скриншот и ваш ID → {owner}",
        "tariff_365_usdt": "🪙 *365 дней — 70 USDT*\n\n📤 Адрес USDT (ERC-20):\n`{usdt}`\n\n⚠️ *Инструкция:*\n1. Отправьте ровно 70 USDT\n2. Сеть: Ethereum (ERC-20)\n3. Отправьте скриншот и ваш ID → {owner}",
        "tariff_30_ton": "💎 *30 дней — 10 TON*\n\n📤 Telegram Wallet:\n`{ton}`\n\n⚠️ *Инструкция:*\n1. Откройте @wallet в Telegram\n2. Отправьте 10 TON на адрес выше\n3. Отправьте скриншот и ваш ID → {owner}",
        "tariff_90_ton": "💎 *90 дней — 25 TON*\n\n📤 Telegram Wallet:\n`{ton}`\n\n⚠️ *Инструкция:*\n1. Откройте @wallet в Telegram\n2. Отправьте 25 TON на адрес выше\n3. Отправьте скриншот и ваш ID → {owner}",
        "tariff_365_ton": "💎 *365 дней — 70 TON*\n\n📤 Telegram Wallet:\n`{ton}`\n\n⚠️ *Инструкция:*\n1. Откройте @wallet в Telegram\n2. Отправьте 70 TON на адрес выше\n3. Отправьте скриншот и ваш ID → {owner}",
    },
    "en": {
        "name": "🇬🇧 English", "choose": "🌐 Choose language:",
        "lang_set": "Language: English", "sub_expired": "⛔ Subscription expired.",
        "wrong_key": "⛔ Invalid key.",
        "welcome_no_access": "👋 *Market Pulse*\n\nSubscription access.\n📱 {owner}",
        "welcome_trial": "👋 *Hello, {name}!*\n🎁 Trial: {days} days.",
        "welcome_back": "👋 *Welcome back, {name}!*\n💳 Subscription: *{days}* days\nLanguage: {lang_name}",
        "profile": "👤 ID: `{uid}`\nSubscription: *{days}* days\nLanguage: {lang_name}\nOwner: {owner}",
        "price": "*{name}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 {ticker} at ${target:.2f} set!",
        "no_alerts": "🔔 No alerts.", "alerts_list": "🔔 *Alerts:*\n\n",
        "del_alert": "✅ {ticker} removed",
        "stock_list": "📋 *Stocks:*\n\n", "crypto_list": "🪙 *Crypto:*\n\n",
        "gainers": "🚀 *Gainers:*\n\n", "losers": "📉 *Losers:*\n\n",
        "potential": "🔮 *Potential:*\n\n", "crypto_potential": "🔮 *Crypto Potential:*\n\n",
        "news": "📰 *News:*\n\n", "no_news": "😴 No movements.",
        "no_candidates": "🔮 No candidates.",
        "help": "ℹ️ Market Pulse\n\n📊 Price | 🪙 Crypto | 📈 RSI | 📉 Chart\n🔔 Alerts | 👤 Profile | 🌐 Language | 💳 Subscribe",
        "enter_ticker": "Enter ticker:", "wrong_ticker": "❌ Invalid ticker",
        "use_buttons": "Use menu.", "main_menu": "Main menu",
        "crypto_menu": "🪙 Crypto", "searching_news": "📰 Searching...",
        "backup_ok": "✅ Backup created.", "backup_fail": "❌ Failed.",
        "log_empty": "Log empty.", "no_users": "No users.",
        "activated": "✅ {uid} activated for {days} days.",
        "notify_activated": "✅ Subscription extended for {days} days!",
        "users_list": "👥 *Users:*\n\n",
        "subscription_info": "💳 *Subscription*\n\nLeft: *{days}* days\n\nChoose payment method:",
        "market_summary": "📊 *Market Summary*\n\n",
        "hype_of_day": "🚀 *Hype of the Day*\n\n",
        "signal_of_day": "🎯 *Signal of the Day*\n\n",
        "top_market_title": "🔥 *Top Market*\n\nSelect section:",
        "btn_top_market": "🔥 Top Market",
        "btn_market_summary": "📊 Market Summary",
        "btn_hype_day": "🚀 Hype of Day",
        "btn_signal_day": "🎯 Signal of Day",
        "btn_us_stocks": "🇺🇸 US Stocks",
        "btn_ru_stocks": "🇷🇺 Russian Stocks",
        "btn_cn_stocks": "🇨🇳 China Stocks",
        "btn_eu_stocks": "🇪🇺 Europe Stocks",
        "btn_crypto_top": "🪙 Crypto Top",
        "btn_price": "📊 Price", "btn_stocks": "📋 Stocks",
        "btn_gainers": "🚀 Gainers", "btn_losers": "📉 Losers",
        "btn_potential": "🔮 Potential", "btn_news": "📰 News",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 Chart",
        "btn_crypto": "🪙 Crypto", "btn_alerts": "🔔 Alerts",
        "btn_profile": "👤 Profile", "btn_subscribe": "💳 Subscribe",
        "btn_help": "ℹ️ Help", "btn_lang": "🌐 Language",
        "btn_crypto_price": "🪙 Price", "btn_crypto_list": "📋 List",
        "btn_crypto_potential": "🔮 Potential", "btn_back": "🔙 Back",
        "btn_tariff_30": "📅 30 d. — 299₽",
        "btn_tariff_90": "📅 90 d. — 699₽",
        "btn_tariff_365": "📅 365 d. — 1999₽",
        "btn_card_pay": "💳 Bank Card (RF)",
        "btn_crypto_pay": "🪙 Crypto (USDT)",
        "btn_ton_pay": "💎 Telegram Wallet (TON)",
        "btn_back_sub": "🔙 Back",
        "crypto_tariff_30": "🪙 30 d. — 10 USDT",
        "crypto_tariff_90": "🪙 90 d. — 25 USDT",
        "crypto_tariff_365": "🪙 365 d. — 70 USDT",
        "ton_tariff_30": "💎 30 d. — 10 TON",
        "ton_tariff_90": "💎 90 d. — 25 TON",
        "ton_tariff_365": "💎 365 d. — 70 TON",
        "tariff_30_card": "📅 *30 days — 299₽*\n\n💳 Card: `{card}`\n\n⚠️ *Instructions:*\n1. Transfer 299₽ to the card\n2. Comment: *«Market Pulse 30 days»*\n3. Send screenshot + your ID → {owner}",
        "tariff_90_card": "📅 *90 days — 699₽*\n\n💳 Card: `{card}`\n\n⚠️ *Instructions:*\n1. Transfer 699₽ to the card\n2. Comment: *«Market Pulse 90 days»*\n3. Send screenshot + your ID → {owner}",
        "tariff_365_card": "📅 *365 days — 1999₽*\n\n💳 Card: `{card}`\n\n⚠️ *Instructions:*\n1. Transfer 1999₽ to the card\n2. Comment: *«Market Pulse 365 days»*\n3. Send screenshot + your ID → {owner}",
        "tariff_30_usdt": "🪙 *30 days — 10 USDT*\n\n📤 USDT (ERC-20):\n`{usdt}`\n\n⚠️ *Instructions:*\n1. Send exactly 10 USDT\n2. Network: Ethereum (ERC-20)\n3. Send screenshot + your ID → {owner}",
        "tariff_90_usdt": "🪙 *90 days — 25 USDT*\n\n📤 USDT (ERC-20):\n`{usdt}`\n\n⚠️ *Instructions:*\n1. Send exactly 25 USDT\n2. Network: Ethereum (ERC-20)\n3. Send screenshot + your ID → {owner}",
        "tariff_365_usdt": "🪙 *365 days — 70 USDT*\n\n📤 USDT (ERC-20):\n`{usdt}`\n\n⚠️ *Instructions:*\n1. Send exactly 70 USDT\n2. Network: Ethereum (ERC-20)\n3. Send screenshot + your ID → {owner}",
        "tariff_30_ton": "💎 *30 days — 10 TON*\n\n📤 Telegram Wallet:\n`{ton}`\n\n⚠️ *Instructions:*\n1. Open @wallet in Telegram\n2. Send 10 TON to the address above\n3. Send screenshot + your ID → {owner}",
        "tariff_90_ton": "💎 *90 days — 25 TON*\n\n📤 Telegram Wallet:\n`{ton}`\n\n⚠️ *Instructions:*\n1. Open @wallet in Telegram\n2. Send 25 TON to the address above\n3. Send screenshot + your ID → {owner}",
        "tariff_365_ton": "💎 *365 days — 70 TON*\n\n📤 Telegram Wallet:\n`{ton}`\n\n⚠️ *Instructions:*\n1. Open @wallet in Telegram\n2. Send 70 TON to the address above\n3. Send screenshot + your ID → {owner}",
    },
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
    code = message.from_user.language_code
    if code and code.startswith("ru"): return LANG["ru"]
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

def extend_user(user_id, days):
    User = Query()
    user = USERS_DB.get(User.id == user_id)
    if user:
        current = datetime.fromisoformat(user["expires"])
        if current < datetime.now(): current = datetime.now()
        USERS_DB.update({"expires": (current + timedelta(days=days)).isoformat()}, User.id == user_id)
    else:
        USERS_DB.insert({"id": user_id, "expires": (datetime.now() + timedelta(days=days)).isoformat()})

def get_price(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params={"range": "2d", "interval": "1d"}, timeout=5)
        data = r.json()["chart"]["result"][0]
        prices = data["indicators"]["quote"][0]["close"]
        current = data["meta"]["regularMarketPrice"]
        prev = prices[-2] if len(prices) >= 2 and prices[-2] else current
        return {"price": current, "change": ((current - prev) / prev) * 100 if prev else 0}
    except:
        return None

def get_crypto_price(symbol):
    try:
        data = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=5).json()
        current, prev = float(data["lastPrice"]), float(data["openPrice"])
        return {"price": current, "change": ((current - prev) / prev) * 100 if prev else 0}
    except:
        return None

def get_rsi(ticker, period=14, is_crypto=False):
    try:
        if is_crypto:
            data = requests.get(f"https://api.binance.com/api/v3/klines?symbol={ticker}&interval=1d&limit=100", timeout=5).json()
            closes = [float(c[4]) for c in data]
        else:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params={"range": "3mo", "interval": "1d"}, timeout=5).json()
            closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [c for c in closes if c is not None]
        if len(closes) < period + 1: return 50
        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(diff if diff > 0 else 0)
            losses.append(-diff if diff < 0 else 0)
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0: return 100
        return round(100 - (100 / (1 + avg_gain / avg_loss)), 1)
    except:
        return 50

def get_news(ticker):
    try:
        data = requests.get(f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}", headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
        return data.get("news", [])[:3]
    except: return []

def get_chart_link(ticker):
    if ticker.endswith(".ME"): return f"https://www.tradingview.com/chart/?symbol=MOEX%3A{ticker.replace('.ME','')}"
    return f"https://www.tradingview.com/chart/?symbol=NASDAQ%3A{ticker}"

def get_crypto_chart_link(symbol):
    return f"https://www.tradingview.com/chart/?symbol=BINANCE%3A{symbol}"

# ─── КОМАНДЫ ВЛАДЕЛЬЦА ──────────────────────────────────
@bot.message_handler(commands=['activate'])
def cmd_activate(message):
    lang = get_lang(message)
    try:
        parts = message.text.split()
        if parts[1] != MASTER_KEY: bot.reply_to(message, lang["wrong_key"]); return
        uid = int(parts[2]); days = int(parts[3]) if len(parts) > 3 else 30
        extend_user(uid, days)
        bot.reply_to(message, lang["activated"].format(uid=uid, days=days))
        bot.send_message(uid, lang["notify_activated"].format(days=days))
    except: bot.reply_to(message, "❌ /activate KEY ID DAYS")

@bot.message_handler(commands=['extend'])
def cmd_extend(message):
    lang = get_lang(message)
    try:
        parts = message.text.split()
        if parts[1] != MASTER_KEY: bot.reply_to(message, lang["wrong_key"]); return
        uid = int(parts[2]); days = int(parts[3])
        extend_user(uid, days)
        bot.reply_to(message, lang["activated"].format(uid=uid, days=days))
        bot.send_message(uid, lang["notify_activated"].format(days=days))
    except: bot.reply_to(message, "❌ /extend KEY ID DAYS")

@bot.message_handler(commands=['users'])
def cmd_users(message):
    lang = get_lang(message)
    parts = message.text.split()
    if len(parts) < 2 or parts[1] != MASTER_KEY: bot.reply_to(message, "⛔ /users KEY"); return
    users = USERS_DB.all()
    if not users: bot.reply_to(message, lang["no_users"]); return
    text = lang["users_list"]
    for u in users:
        exp = datetime.fromisoformat(u["expires"])
        days = (exp - datetime.now()).days
        text += f"{'✅' if days > 0 else '❌'} `{u['id']}` | {max(0, days)} d.\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['backup'])
def cmd_backup(message):
    lang = get_lang(message)
    parts = message.text.split()
    if len(parts) < 2 or parts[1] != MASTER_KEY: bot.reply_to(message, "⛔ /backup KEY"); return
    try:
        shutil.copy("users.json", "backup_users.json")
        bot.reply_to(message, lang["backup_ok"])
    except: bot.reply_to(message, lang["backup_fail"])

# ─── СТАРТ ──────────────────────────────────────────────
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
        text = lang["welcome_back"].format(name=message.from_user.first_name, days=days, lang_name=lang["name"])
    
    bot.send_message(uid, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def main_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(lang["btn_top_market"]), types.KeyboardButton(lang["btn_stocks"]),
        types.KeyboardButton(lang["btn_gainers"]), types.KeyboardButton(lang["btn_losers"]),
        types.KeyboardButton(lang["btn_potential"]), types.KeyboardButton(lang["btn_news"]),
        types.KeyboardButton(lang["btn_rsi"]), types.KeyboardButton(lang["btn_chart"]),
        types.KeyboardButton(lang["btn_crypto"]), types.KeyboardButton(lang["btn_alerts"]),
        types.KeyboardButton(lang["btn_profile"]), types.KeyboardButton(lang["btn_subscribe"]),
        types.KeyboardButton(lang["btn_lang"]), types.KeyboardButton(lang["btn_help"])
    )
    return markup

def top_market_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(lang["btn_market_summary"]),
        types.KeyboardButton(lang["btn_hype_day"]),
        types.KeyboardButton(lang["btn_signal_day"]),
        types.KeyboardButton(lang["btn_us_stocks"]),
        types.KeyboardButton(lang["btn_ru_stocks"]),
        types.KeyboardButton(lang["btn_cn_stocks"]),
        types.KeyboardButton(lang["btn_eu_stocks"]),
        types.KeyboardButton(lang["btn_crypto_top"]),
        types.KeyboardButton(lang["btn_back"])
    )
    return markup

def crypto_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(lang["btn_crypto_price"]), types.KeyboardButton(lang["btn_crypto_list"]),
        types.KeyboardButton(lang["btn_crypto_potential"]), types.KeyboardButton(lang["btn_back"])
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
        text = lang["welcome_back"].format(name=call.from_user.first_name, days=days, lang_name=lang["name"])
        bot.send_message(uid, text, parse_mode="Markdown", reply_markup=main_menu(lang))
    else:
        bot.send_message(uid, lang["welcome_no_access"].format(owner=OWNER_USERNAME), parse_mode="Markdown")

# ─── КОМАНДЫ ────────────────────────────────────────────
@bot.message_handler(commands=['price'])
def send_price(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    try:
        t = message.text.split()[1].upper()
        d = get_crypto_price(t) if t.endswith("USDT") else get_price(t)
        if d is None: bot.reply_to(message, lang["wrong_ticker"]); return
        e = "📈" if d["change"] >= 0 else "📉"
        bot.send_message(message.chat.id, lang["price"].format(name=t, price=d["price"], emoji=e, change=d["change"]), parse_mode="Markdown", reply_markup=main_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"])

@bot.message_handler(commands=['rsi'])
def cmd_rsi(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    try:
        t = message.text.split()[1].upper()
        ic = t.endswith("USDT")
        d = get_crypto_price(t) if ic else get_price(t)
        if d is None: bot.reply_to(message, lang["wrong_ticker"]); return
        r = get_rsi(t, is_crypto=ic)
        s = "🔴" if r>=70 else "🟢" if r<=30 else "⚪" if 40<=r<=60 else "🟠" if r>60 else "🟡"
        bot.send_message(message.chat.id, lang["rsi"].format(ticker=t, price=d["price"], rsi=r, signal=s), parse_mode="Markdown", reply_markup=main_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"])

@bot.message_handler(commands=['chart'])
def cmd_chart(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    try:
        t = message.text.split()[1].upper()
        if t.endswith("USDT"): d = get_crypto_price(t); l = get_crypto_chart_link(t)
        else: d = get_price(t); l = get_chart_link(t)
        if d is None: bot.reply_to(message, lang["wrong_ticker"]); return
        bot.send_message(message.chat.id, lang["chart"].format(ticker=t, price=d["price"], link=l), parse_mode="Markdown", reply_markup=main_menu(lang), disable_web_page_preview=False)
    except: bot.reply_to(message, lang["wrong_ticker"])

@bot.message_handler(commands=['alert'])
def cmd_alert(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    try:
        p = message.text.split(); t, target = p[1].upper(), float(p[2])
        ic = t.endswith("USDT")
        cur = get_crypto_price(t)["price"] if ic else get_price(t)["price"]
        alerts = json.load(open("alerts.json")) if os.path.exists("alerts.json") else []
        alerts.append({"chat_id": message.chat.id, "ticker": t, "target": target, "direction": "above" if target > cur else "below", "is_crypto": ic})
        json.dump(alerts, open("alerts.json", "w"))
        bot.reply_to(message, lang["alert_set"].format(ticker=t, target=target), reply_markup=main_menu(lang))
    except: bot.reply_to(message, "❌ /alert TICKER PRICE")

@bot.message_handler(commands=['alerts'])
def cmd_alerts(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    alerts = json.load(open("alerts.json")) if os.path.exists("alerts.json") else []
    my = [a for a in alerts if a["chat_id"] == message.chat.id]
    if not my: bot.reply_to(message, lang["no_alerts"], reply_markup=main_menu(lang)); return
    text = lang["alerts_list"]
    for i, a in enumerate(my, 1):
        try:
            price = get_crypto_price(a["ticker"])["price"] if a.get("is_crypto") else get_price(a["ticker"])["price"]
            text += f"{i}. *{a['ticker']}*: target ${a['target']:.2f} | now ${price:.2f}\n"
        except: text += f"{i}. *{a['ticker']}*: target ${a['target']:.2f}\n"
    text += "\n/delalert NUMBER"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

@bot.message_handler(commands=['delalert'])
def cmd_delalert(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    try:
        idx = int(message.text.split()[1]) - 1
        alerts = json.load(open("alerts.json")) if os.path.exists("alerts.json") else []
        my = [a for a in alerts if a["chat_id"] == message.chat.id]
        if idx < 0 or idx >= len(my): bot.reply_to(message, "❌"); return
        removed = my[idx]; alerts.remove(removed); json.dump(alerts, open("alerts.json", "w"))
        bot.reply_to(message, lang["del_alert"].format(ticker=removed["ticker"]), reply_markup=main_menu(lang))
    except: bot.reply_to(message, "❌ /delalert NUMBER")

@bot.message_handler(commands=['me'])
def cmd_me(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    uid = message.from_user.id
    bot.send_message(uid, lang["profile"].format(uid=uid, days=days_left(uid), lang_name=lang["name"], owner=OWNER_USERNAME), parse_mode="Markdown", reply_markup=main_menu(lang))

@bot.message_handler(commands=['lang'])
def cmd_lang(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    bot.send_message(message.chat.id, lang["choose"], reply_markup=lang_menu())

# ─── КНОПКИ ──────────────────────────────────────────────
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
    
    t = message.text
    
    # Главное меню
    if t == lang["btn_top_market"]:
        bot.send_message(uid, lang["top_market_title"], parse_mode="Markdown", reply_markup=top_market_menu(lang))
    elif t == lang["btn_stocks"]: show_watchlist(message, lang)
    elif t == lang["btn_gainers"]: show_top_gainers(message, lang)
    elif t == lang["btn_losers"]: show_top_losers(message, lang)
    elif t == lang["btn_potential"]: show_potential(message, lang)
    elif t == lang["btn_news"]: show_news_movers(message, lang)
    elif t == lang["btn_rsi"]:
        msg = bot.reply_to(message, lang["enter_ticker"], reply_markup=types.ForceReply(selective=True))
        bot.register_next_step_handler(msg, lambda m: process_rsi(m, lang))
    elif t == lang["btn_chart"]:
        msg = bot.reply_to(message, lang["enter_ticker"], reply_markup=types.ForceReply(selective=True))
        bot.register_next_step_handler(msg, lambda m: process_chart(m, lang))
    elif t == lang["btn_crypto"]: bot.send_message(uid, lang["crypto_menu"], reply_markup=crypto_menu(lang))
    elif t == lang["btn_crypto_price"]:
        msg = bot.reply_to(message, lang["enter_ticker"], reply_markup=types.ForceReply(selective=True))
        bot.register_next_step_handler(msg, lambda m: process_crypto_ticker(m, lang))
    elif t == lang["btn_crypto_list"]: show_crypto_list(message, lang)
    elif t == lang["btn_crypto_potential"]: show_crypto_potential(message, lang)
    elif t == lang["btn_alerts"]: cmd_alerts(message)
    elif t == lang["btn_profile"]: cmd_me(message)
    elif t == lang["btn_subscribe"]: show_payment_options(message, lang)
    elif t == lang["btn_help"]: bot.send_message(uid, lang["help"], parse_mode="Markdown", reply_markup=main_menu(lang))
    
    # Топ рынка
    elif t == lang["btn_market_summary"]: show_market_summary(message, lang)
    elif t == lang["btn_hype_day"]: show_hype_of_day(message, lang)
    elif t == lang["btn_signal_day"]: show_signal_of_day(message, lang)
    elif t == lang["btn_us_stocks"]: show_stock_group(message, lang, US_STOCKS, "🇺🇸 Акции США")
    elif t == lang["btn_ru_stocks"]: show_stock_group(message, lang, RU_STOCKS, "🇷🇺 Акции РФ")
    elif t == lang["btn_cn_stocks"]: show_stock_group(message, lang, CN_STOCKS, "🇨🇳 Акции Китая")
    elif t == lang["btn_eu_stocks"]: show_stock_group(message, lang, EU_STOCKS, "🇪🇺 Акции Европы")
    elif t == lang["btn_crypto_top"]: show_stock_group(message, lang, TOP_CRYPTO, "🪙 Крипто-топ", is_crypto=True)
    
    # Назад
    elif t == lang["btn_back"]: bot.send_message(uid, lang["main_menu"], reply_markup=main_menu(lang))
    
    # Оплата
    elif t == lang["btn_card_pay"]: show_card_tariffs(message, lang)
    elif t == lang["btn_crypto_pay"]: show_usdt_tariffs(message, lang)
    elif t == lang["btn_ton_pay"]: show_ton_tariffs(message, lang)
    elif t == lang["btn_tariff_30"]: show_tariff_card(message, lang, 30, 299)
    elif t == lang["btn_tariff_90"]: show_tariff_card(message, lang, 90, 699)
    elif t == lang["btn_tariff_365"]: show_tariff_card(message, lang, 365, 1999)
    elif t == lang["crypto_tariff_30"]: show_tariff_usdt(message, lang, 30, 10)
    elif t == lang["crypto_tariff_90"]: show_tariff_usdt(message, lang, 90, 25)
    elif t == lang["crypto_tariff_365"]: show_tariff_usdt(message, lang, 365, 70)
    elif t == lang["ton_tariff_30"]: show_tariff_ton(message, lang, 30, 10)
    elif t == lang["ton_tariff_90"]: show_tariff_ton(message, lang, 90, 25)
    elif t == lang["ton_tariff_365"]: show_tariff_ton(message, lang, 365, 70)
    elif t == lang["btn_back_sub"]: bot.send_message(uid, lang["main_menu"], reply_markup=main_menu(lang))
    
    else:
        try:
            tick = t.upper()
            d = get_crypto_price(tick) if tick.endswith("USDT") else get_price(tick)
            if d is None: bot.reply_to(message, lang["use_buttons"], reply_markup=main_menu(lang)); return
            e = "📈" if d["change"]>=0 else "📉"
            bot.send_message(uid, lang["price"].format(name=tick, price=d["price"], emoji=e, change=d["change"]), parse_mode="Markdown", reply_markup=main_menu(lang))
        except: bot.reply_to(message, lang["use_buttons"], reply_markup=main_menu(lang))

# ─── ТОП РЫНКА ──────────────────────────────────────────
def show_market_summary(message, lang):
    text = lang["market_summary"]
    for name, ticker in INDICES.items():
        d = get_price(ticker)
        if d:
            e = "📈" if d["change"]>=0 else "📉"
            text += f"{name}: ${d['price']:.2f} {e} {d['change']:+.2f}%\n"
        else:
            text += f"{name}: ❌\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=top_market_menu(lang))

def show_hype_of_day(message, lang):
    try:
        best = None
        best_change = 0
        all_stocks = list(US_STOCKS.values()) + list(RU_STOCKS.values())
        for ticker in all_stocks[:10]:
            d = get_price(ticker)
            if d and abs(d["change"]) > abs(best_change):
                best_change = d["change"]
                best = {"name": ticker, "price": d["price"], "change": d["change"]}
        
        if best:
            e = "📈" if best["change"]>=0 else "📉"
            text = lang["hype_of_day"] + f"*{best['name']}*\n💰 ${best['price']:.2f} {e} {best['change']:+.2f}%\n🔥 Самое сильное движение сегодня"
        else:
            text = lang["hype_of_day"] + "Рынок спокоен. Нет резких движений."
    except:
        text = lang["hype_of_day"] + "Ошибка загрузки. Попробуйте позже."
    text += "\n━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=top_market_menu(lang))

def show_signal_of_day(message, lang):
    try:
        best = None
        best_rsi = 100
        for ticker in WATCHLIST:
            rsi = get_rsi(ticker)
            d = get_price(ticker)
            if d and rsi < best_rsi:
                best_rsi = rsi
                best = {"name": ticker, "price": d["price"], "change": d["change"], "rsi": rsi}
        
        if best:
            s = "🟢" if best["rsi"]<=30 else "🟡"
            text = lang["signal_of_day"] + f"*{best['name']}*\n💰 ${best['price']:.2f}\n📊 RSI: *{best['rsi']}* {s}\n\n_RSI ниже 30 — сигнал к покупке_"
        else:
            text = lang["signal_of_day"] + "Нет данных."
    except:
        text = lang["signal_of_day"] + "Ошибка загрузки."
    text += "\n━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=top_market_menu(lang))

def show_stock_group(message, lang, stock_dict, title, is_crypto=False):
    text = f"*{title}*\n\n"
    for name, ticker in stock_dict.items():
        d = get_crypto_price(ticker) if is_crypto else get_price(ticker)
        if d:
            e = "📈" if d["change"]>=0 else "📉"
            text += f"{name}: ${d['price']:.2f} {e} {d['change']:+.2f}%\n"
        else:
            text += f"{name}: ❌\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=top_market_menu(lang))

# ─── МЕНЮ ОПЛАТЫ ────────────────────────────────────────
def show_payment_options(message, lang):
    days = days_left(message.from_user.id)
    text = lang["subscription_info"].format(days=days)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton(lang["btn_card_pay"]),
        types.KeyboardButton(lang["btn_crypto_pay"]),
        types.KeyboardButton(lang["btn_ton_pay"]),
        types.KeyboardButton(lang["btn_back_sub"])
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

def show_card_tariffs(message, lang):
    text = "💳 *Оплата картой (РФ)*\n\nВыберите тариф:"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton(lang["btn_tariff_30"]),
        types.KeyboardButton(lang["btn_tariff_90"]),
        types.KeyboardButton(lang["btn_tariff_365"]),
        types.KeyboardButton(lang["btn_back_sub"])
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

def show_usdt_tariffs(message, lang):
    text = "🪙 *Оплата USDT (ERC-20)*\n\nВыберите тариф:"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton(lang["crypto_tariff_30"]),
        types.KeyboardButton(lang["crypto_tariff_90"]),
        types.KeyboardButton(lang["crypto_tariff_365"]),
        types.KeyboardButton(lang["btn_back_sub"])
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

def show_ton_tariffs(message, lang):
    text = "💎 *Оплата Telegram Wallet (TON)*\n\nВыберите тариф:"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton(lang["ton_tariff_30"]),
        types.KeyboardButton(lang["ton_tariff_90"]),
        types.KeyboardButton(lang["ton_tariff_365"]),
        types.KeyboardButton(lang["btn_back_sub"])
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

def show_tariff_card(message, lang, days, price):
    key = f"tariff_{days}_card"
    text = lang[key].format(card=CARD_NUMBER, owner=OWNER_USERNAME)
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_tariff_usdt(message, lang, days, amount):
    key = f"tariff_{days}_usdt"
    text = lang[key].format(usdt=USDT_ADDRESS, owner=OWNER_USERNAME)
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_tariff_ton(message, lang, days, amount):
    key = f"tariff_{days}_ton"
    text = lang[key].format(ton=TON_ADDRESS, owner=OWNER_USERNAME)
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

# ─── ОБРАБОТЧИКИ ────────────────────────────────────────
def process_ticker(message, lang):
    try:
        t = message.text.upper()
        d = get_crypto_price(t) if t.endswith("USDT") else get_price(t)
        if d is None: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang)); return
        e = "📈" if d["change"]>=0 else "📉"
        bot.send_message(message.chat.id, lang["price"].format(name=t, price=d["price"], emoji=e, change=d["change"]), parse_mode="Markdown", reply_markup=main_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang))

def process_crypto_ticker(message, lang):
    try:
        t = message.text.upper(); d = get_crypto_price(t)
        if d is None: bot.reply_to(message, lang["wrong_ticker"], reply_markup=crypto_menu(lang)); return
        e = "📈" if d["change"]>=0 else "📉"
        bot.send_message(message.chat.id, lang["price"].format(name=t, price=d["price"], emoji=e, change=d["change"]), parse_mode="Markdown", reply_markup=crypto_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"], reply_markup=crypto_menu(lang))

def process_rsi(message, lang):
    try:
        t = message.text.upper(); ic = t.endswith("USDT")
        d = get_crypto_price(t) if ic else get_price(t)
        if d is None: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang)); return
        r = get_rsi(t, is_crypto=ic)
        s = "🔴" if r>=70 else "🟢" if r<=30 else "⚪" if 40<=r<=60 else "🟠" if r>60 else "🟡"
        bot.send_message(message.chat.id, lang["rsi"].format(ticker=t, price=d["price"], rsi=r, signal=s), parse_mode="Markdown", reply_markup=main_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang))

def process_chart(message, lang):
    try:
        t = message.text.upper()
        if t.endswith("USDT"): d = get_crypto_price(t); l = get_crypto_chart_link(t)
        else: d = get_price(t); l = get_chart_link(t)
        if d is None: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang)); return
        bot.send_message(message.chat.id, lang["chart"].format(ticker=t, price=d["price"], link=l), parse_mode="Markdown", reply_markup=main_menu(lang), disable_web_page_preview=False)
    except: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang))

def show_watchlist(message, lang):
    text = lang["stock_list"]
    for t in WATCHLIST:
        d = get_price(t)
        if d:
            text += f"• *{t}*: ${d['price']:.2f} {'📈' if d['change']>=0 else '📉'} {d['change']:+.2f}%\n"
        else: text += f"• *{t}*: ❌\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_top_gainers(message, lang):
    dl = []
    for t in WATCHLIST:
        d = get_price(t)
        if d: d["ticker"] = t; dl.append(d)
    dl.sort(key=lambda x: x["change"], reverse=True)
    text = lang["gainers"]
    for i, d in enumerate(dl[:5], 1): text += f"{i}. *{d['ticker']}*: +{d['change']:.2f}%\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_top_losers(message, lang):
    dl = []
    for t in WATCHLIST:
        d = get_price(t)
        if d: d["ticker"] = t; dl.append(d)
    dl.sort(key=lambda x: x["change"])
    text = lang["losers"]
    for i, d in enumerate(dl[:5], 1): text += f"{i}. *{d['ticker']}*: {d['change']:.2f}%\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_potential(message, lang):
    dl = []
    for t in WATCHLIST:
        d = get_price(t)
        if d: dl.append({"ticker": t, "rsi": get_rsi(t), "price": d["price"]})
    dl.sort(key=lambda x: x["rsi"])
    pot = [d for d in dl if d["rsi"] < 45][:5]
    text = (lang["potential"] + "\n".join(f"{'🟢' if d['rsi']<30 else '🟡'} *{d['ticker']}*: RSI {d['rsi']} | ${d['price']:.2f}" for d in pot)) if pot else lang["no_candidates"]
    text += "\n━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_news_movers(message, lang):
    bot.send_message(message.chat.id, lang["searching_news"])
    mv = []
    for t in WATCHLIST:
        d = get_price(t)
        if d and abs(d["change"]) > 1.5: mv.append({"ticker": t, "change": d["change"], "price": d["price"], "news": get_news(t)})
    if not mv: bot.send_message(message.chat.id, lang["no_news"], reply_markup=main_menu(lang)); return
    mv.sort(key=lambda x: abs(x["change"]), reverse=True)
    text = lang["news"]
    for m in mv[:5]:
        text += f"{'📈' if m['change']>=0 else '📉'} *{m['ticker']}*: {m['change']:+.2f}%\n"
        for n in m["news"][:2]: text += f"  📎 [{n.get('title','')[:80]}]({n.get('link','')})\n"
        text += "\n"
    text += "━━━━━━━━━━━━━━━"
    if len(text) > 4000:
        for p in [text[i:i+3800] for i in range(0, len(text), 3800)]:
            bot.send_message(message.chat.id, p, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang), disable_web_page_preview=True)

def show_crypto_list(message, lang):
    text = lang["crypto_list"]
    for t in CRYPTO_LIST:
        d = get_crypto_price(t)
        if d: text += f"• *{t.replace('USDT','')}*: ${d['price']:.2f} {'📈' if d['change']>=0 else '📉'} {d['change']:+.2f}%\n"
        else: text += f"• *{t}*: ❌\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=crypto_menu(lang))

def show_crypto_potential(message, lang):
    dl = []
    for t in CRYPTO_LIST:
        d = get_crypto_price(t)
        if d: dl.append({"ticker": t.replace("USDT",""), "rsi": get_rsi(t, is_crypto=True), "price": d["price"]})
    dl.sort(key=lambda x: x["rsi"])
    pot = [d for d in dl if d["rsi"] < 45][:5]
    text = (lang["crypto_potential"] + "\n".join(f"{'🟢' if d['rsi']<30 else '🟡'} *{d['ticker']}*: RSI {d['rsi']} | ${d['price']:.2f}" for d in pot)) if pot else lang["no_candidates"]
    text += "\n━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=crypto_menu(lang))

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
