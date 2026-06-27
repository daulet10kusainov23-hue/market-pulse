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
        "wrong_key": "⛔ Неверный ключ.",
        "welcome_no_access": "👋 *Market Pulse*\n\nДоступ по подписке.\n📱 {owner}",
        "welcome_trial": "👋 *Привет, {name}!*\n🎁 Пробный период: {days} дн.",
        "welcome_back": "👋 *С возвращением, {name}!*\n💳 Подписка: *{days}* дн.\nЯзык: {lang_name}",
        "profile": "👤 ID: `{uid}`\nПодписка: *{days}* дн.\nЯзык: {lang_name}\nВладелец: {owner}",
        "price": "*{ticker}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 {ticker} на ${target:.2f} установлен!",
        "no_alerts": "🔔 Нет алертов.",
        "alerts_list": "🔔 *Алерты:*\n\n",
        "del_alert": "✅ {ticker} удалён",
        "stock_list": "📋 *Акции:*\n\n",
        "crypto_list": "🪙 *Крипта:*\n\n",
        "gainers": "🚀 *Рост:*\n\n",
        "losers": "📉 *Падение:*\n\n",
        "potential": "🔮 *Потенциал:*\n\n",
        "crypto_potential": "🔮 *Крипто потенциал:*\n\n",
        "news": "📰 *Новости:*\n\n",
        "no_news": "😴 Нет движений.",
        "no_candidates": "🔮 Нет кандидатов.",
        "help": "ℹ️ Market Pulse\n\n📊 Цена | 🪙 Крипта | 📈 RSI | 📉 График\n🔔 Алерты | 👤 Профиль | 🌐 Язык | 💳 Подписка",
        "enter_ticker": "Введи тикер:",
        "wrong_ticker": "❌ Неверный тикер",
        "use_buttons": "Используй меню.",
        "main_menu": "Главное меню",
        "crypto_menu": "🪙 Крипта",
        "searching_news": "📰 Ищу новости...",
        "backup_ok": "✅ Бекап создан.",
        "backup_fail": "❌ Ошибка.",
        "log_empty": "Лог пуст.",
        "no_users": "Нет пользователей.",
        "activated": "✅ {uid} активирован на {days} дн.",
        "notify_activated": "✅ Подписка продлена на {days} дней!",
        "users_list": "👥 *Пользователи:*\n\n",
        "subscription_info": "💳 Подписка: *{days}* дн.\n\nДля продления: {owner}",
        "btn_price": "📊 Цена", "btn_stocks": "📋 Акции",
        "btn_gainers": "🚀 Рост", "btn_losers": "📉 Падение",
        "btn_potential": "🔮 Потенциал", "btn_news": "📰 Новости",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 График",
        "btn_crypto": "🪙 Крипта", "btn_alerts": "🔔 Алерты",
        "btn_profile": "👤 Профиль", "btn_subscribe": "💳 Подписка",
        "btn_help": "ℹ️ Помощь", "btn_lang": "🌐 Язык",
        "btn_crypto_price": "🪙 Курс", "btn_crypto_list": "📋 Список",
        "btn_crypto_potential": "🔮 Потенциал", "btn_back": "🔙 Назад",
    },
    "en": {
        "name": "🇬🇧 English", "choose": "🌐 Choose language:",
        "lang_set": "Language: English", "sub_expired": "⛔ Subscription expired.",
        "wrong_key": "⛔ Invalid key.",
        "welcome_no_access": "👋 *Market Pulse*\n\nSubscription access.\n📱 {owner}",
        "welcome_trial": "👋 *Hello, {name}!*\n🎁 Trial: {days} days.",
        "welcome_back": "👋 *Welcome back, {name}!*\n💳 Subscription: *{days}* days\nLanguage: {lang_name}",
        "profile": "👤 ID: `{uid}`\nSubscription: *{days}* days\nLanguage: {lang_name}\nOwner: {owner}",
        "price": "*{ticker}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 {ticker} at ${target:.2f} set!",
        "no_alerts": "🔔 No alerts.",
        "alerts_list": "🔔 *Alerts:*\n\n",
        "del_alert": "✅ {ticker} removed",
        "stock_list": "📋 *Stocks:*\n\n",
        "crypto_list": "🪙 *Crypto:*\n\n",
        "gainers": "🚀 *Gainers:*\n\n",
        "losers": "📉 *Losers:*\n\n",
        "potential": "🔮 *Potential:*\n\n",
        "crypto_potential": "🔮 *Crypto Potential:*\n\n",
        "news": "📰 *News:*\n\n",
        "no_news": "😴 No movements.",
        "no_candidates": "🔮 No candidates.",
        "help": "ℹ️ Market Pulse\n\n📊 Price | 🪙 Crypto | 📈 RSI | 📉 Chart\n🔔 Alerts | 👤 Profile | 🌐 Language | 💳 Subscribe",
        "enter_ticker": "Enter ticker:",
        "wrong_ticker": "❌ Invalid ticker",
        "use_buttons": "Use menu.",
        "main_menu": "Main menu",
        "crypto_menu": "🪙 Crypto",
        "searching_news": "📰 Searching...",
        "backup_ok": "✅ Backup created.",
        "backup_fail": "❌ Failed.",
        "log_empty": "Log empty.",
        "no_users": "No users.",
        "activated": "✅ {uid} activated for {days} days.",
        "notify_activated": "✅ Subscription extended for {days} days!",
        "users_list": "👥 *Users:*\n\n",
        "subscription_info": "💳 Subscription: *{days}* days\n\nContact: {owner}",
        "btn_price": "📊 Price", "btn_stocks": "📋 Stocks",
        "btn_gainers": "🚀 Gainers", "btn_losers": "📉 Losers",
        "btn_potential": "🔮 Potential", "btn_news": "📰 News",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 Chart",
        "btn_crypto": "🪙 Crypto", "btn_alerts": "🔔 Alerts",
        "btn_profile": "👤 Profile", "btn_subscribe": "💳 Subscribe",
        "btn_help": "ℹ️ Help", "btn_lang": "🌐 Language",
        "btn_crypto_price": "🪙 Price", "btn_crypto_list": "📋 List",
        "btn_crypto_potential": "🔮 Potential", "btn_back": "🔙 Back",
    },
    "zh": {
        "name": "🇨🇳 中文", "choose": "🌐 选择语言：",
        "lang_set": "语言：中文", "sub_expired": "⛔ 订阅已过期。",
        "wrong_key": "⛔ 密钥无效。",
        "welcome_no_access": "👋 *Market Pulse*\n\n订阅访问。\n📱 {owner}",
        "welcome_trial": "👋 *你好，{name}！*\n🎁 试用：{days} 天。",
        "welcome_back": "👋 *欢迎回来，{name}！*\n💳 订阅：*{days}* 天\n语言：{lang_name}",
        "profile": "👤 ID: `{uid}`\n订阅: *{days}* 天\n语言: {lang_name}\n所有者: {owner}",
        "price": "*{ticker}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 {ticker} ${target:.2f} 已设置！",
        "no_alerts": "🔔 无警报。",
        "alerts_list": "🔔 *警报：*\n\n",
        "del_alert": "✅ {ticker} 已删除",
        "stock_list": "📋 *股票：*\n\n",
        "crypto_list": "🪙 *加密货币：*\n\n",
        "gainers": "🚀 *涨幅：*\n\n",
        "losers": "📉 *跌幅：*\n\n",
        "potential": "🔮 *潜力：*\n\n",
        "crypto_potential": "🔮 *加密货币潜力：*\n\n",
        "news": "📰 *新闻：*\n\n",
        "no_news": "😴 无波动。",
        "no_candidates": "🔮 无候选。",
        "help": "ℹ️ Market Pulse\n\n📊 价格 | 🪙 加密货币 | 📈 RSI | 📉 图表\n🔔 警报 | 👤 个人 | 🌐 语言 | 💳 订阅",
        "enter_ticker": "输入代码：",
        "wrong_ticker": "❌ 无效代码",
        "use_buttons": "使用菜单。",
        "main_menu": "主菜单",
        "crypto_menu": "🪙 加密货币",
        "searching_news": "📰 搜索...",
        "backup_ok": "✅ 备份完成。",
        "backup_fail": "❌ 失败。",
        "log_empty": "日志为空。",
        "no_users": "无用户。",
        "activated": "✅ {uid} 已激活 {days} 天。",
        "notify_activated": "✅ 订阅已延长 {days} 天！",
        "users_list": "👥 *用户：*\n\n",
        "subscription_info": "💳 订阅: *{days}* 天\n\n联系: {owner}",
        "btn_price": "📊 价格", "btn_stocks": "📋 股票",
        "btn_gainers": "🚀 涨幅", "btn_losers": "📉 跌幅",
        "btn_potential": "🔮 潜力", "btn_news": "📰 新闻",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 图表",
        "btn_crypto": "🪙 加密货币", "btn_alerts": "🔔 警报",
        "btn_profile": "👤 个人", "btn_subscribe": "💳 订阅",
        "btn_help": "ℹ️ 帮助", "btn_lang": "🌐 语言",
        "btn_crypto_price": "🪙 价格", "btn_crypto_list": "📋 列表",
        "btn_crypto_potential": "🔮 潜力", "btn_back": "🔙 返回",
    },
    "fr": {
        "name": "🇫🇷 Français", "choose": "🌐 Choisissez la langue :",
        "lang_set": "Langue : Français", "sub_expired": "⛔ Abonnement expiré.",
        "wrong_key": "⛔ Clé invalide.",
        "welcome_no_access": "👋 *Market Pulse*\n\nAccès par abonnement.\n📱 {owner}",
        "welcome_trial": "👋 *Bonjour, {name} !*\n🎁 Essai : {days} jours.",
        "welcome_back": "👋 *Bon retour, {name} !*\n💳 Abonnement : *{days}* jours\nLangue : {lang_name}",
        "profile": "👤 ID: `{uid}`\nAbonnement: *{days}* jours\nLangue: {lang_name}\nPropriétaire: {owner}",
        "price": "*{ticker}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 {ticker} à ${target:.2f} !",
        "no_alerts": "🔔 Aucune alerte.",
        "alerts_list": "🔔 *Alertes :*\n\n",
        "del_alert": "✅ {ticker} supprimé",
        "stock_list": "📋 *Actions :*\n\n",
        "crypto_list": "🪙 *Crypto :*\n\n",
        "gainers": "🚀 *Hausses :*\n\n",
        "losers": "📉 *Baisses :*\n\n",
        "potential": "🔮 *Potentiel :*\n\n",
        "crypto_potential": "🔮 *Potentiel crypto :*\n\n",
        "news": "📰 *Actualités :*\n\n",
        "no_news": "😴 Pas de mouvements.",
        "no_candidates": "🔮 Aucun candidat.",
        "help": "ℹ️ Market Pulse\n\n📊 Prix | 🪙 Crypto | 📈 RSI | 📉 Graphique\n🔔 Alertes | 👤 Profil | 🌐 Langue | 💳 Abonnement",
        "enter_ticker": "Entrez le ticker :",
        "wrong_ticker": "❌ Invalide",
        "use_buttons": "Utilisez le menu.",
        "main_menu": "Menu principal",
        "crypto_menu": "🪙 Crypto",
        "searching_news": "📰 Recherche...",
        "backup_ok": "✅ Sauvegarde créée.",
        "backup_fail": "❌ Échec.",
        "log_empty": "Journal vide.",
        "no_users": "Aucun utilisateur.",
        "activated": "✅ {uid} activé {days} jours.",
        "notify_activated": "✅ Abonnement prolongé de {days} jours !",
        "users_list": "👥 *Utilisateurs :*\n\n",
        "subscription_info": "💳 Abonnement: *{days}* jours\n\nContact: {owner}",
        "btn_price": "📊 Prix", "btn_stocks": "📋 Actions",
        "btn_gainers": "🚀 Hausses", "btn_losers": "📉 Baisses",
        "btn_potential": "🔮 Potentiel", "btn_news": "📰 Actualités",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 Graphique",
        "btn_crypto": "🪙 Crypto", "btn_alerts": "🔔 Alertes",
        "btn_profile": "👤 Profil", "btn_subscribe": "💳 Abonnement",
        "btn_help": "ℹ️ Aide", "btn_lang": "🌐 Langue",
        "btn_crypto_price": "🪙 Prix", "btn_crypto_list": "📋 Liste",
        "btn_crypto_potential": "🔮 Potentiel", "btn_back": "🔙 Retour",
    },
    "de": {
        "name": "🇩🇪 Deutsch", "choose": "🌐 Sprache wählen:",
        "lang_set": "Sprache: Deutsch", "sub_expired": "⛔ Abonnement abgelaufen.",
        "wrong_key": "⛔ Ungültiger Schlüssel.",
        "welcome_no_access": "👋 *Market Pulse*\n\nZugang per Abo.\n📱 {owner}",
        "welcome_trial": "👋 *Hallo, {name}!*\n🎁 Test: {days} Tage.",
        "welcome_back": "👋 *Willkommen zurück, {name}!*\n💳 Abo: *{days}* Tage\nSprache: {lang_name}",
        "profile": "👤 ID: `{uid}`\nAbo: *{days}* Tage\nSprache: {lang_name}\nBesitzer: {owner}",
        "price": "*{ticker}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 {ticker} bei ${target:.2f}!",
        "no_alerts": "🔔 Keine Alarme.",
        "alerts_list": "🔔 *Alarme:*\n\n",
        "del_alert": "✅ {ticker} entfernt",
        "stock_list": "📋 *Aktien:*\n\n",
        "crypto_list": "🪙 *Krypto:*\n\n",
        "gainers": "🚀 *Gewinner:*\n\n",
        "losers": "📉 *Verlierer:*\n\n",
        "potential": "🔮 *Potenzial:*\n\n",
        "crypto_potential": "🔮 *Krypto-Potenzial:*\n\n",
        "news": "📰 *Nachrichten:*\n\n",
        "no_news": "😴 Keine Bewegungen.",
        "no_candidates": "🔮 Keine Kandidaten.",
        "help": "ℹ️ Market Pulse\n\n📊 Preis | 🪙 Krypto | 📈 RSI | 📉 Chart\n🔔 Alarme | 👤 Profil | 🌐 Sprache | 💳 Abo",
        "enter_ticker": "Ticker:",
        "wrong_ticker": "❌ Ungültig",
        "use_buttons": "Menü verwenden.",
        "main_menu": "Hauptmenü",
        "crypto_menu": "🪙 Krypto",
        "searching_news": "📰 Suche...",
        "backup_ok": "✅ Backup erstellt.",
        "backup_fail": "❌ Fehler.",
        "log_empty": "Log leer.",
        "no_users": "Keine Benutzer.",
        "activated": "✅ {uid} aktiviert {days} Tage.",
        "notify_activated": "✅ Abo um {days} Tage verlängert!",
        "users_list": "👥 *Benutzer:*\n\n",
        "subscription_info": "💳 Abo: *{days}* Tage\n\nKontakt: {owner}",
        "btn_price": "📊 Preis", "btn_stocks": "📋 Aktien",
        "btn_gainers": "🚀 Gewinner", "btn_losers": "📉 Verlierer",
        "btn_potential": "🔮 Potenzial", "btn_news": "📰 Nachrichten",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 Chart",
        "btn_crypto": "🪙 Krypto", "btn_alerts": "🔔 Alarme",
        "btn_profile": "👤 Profil", "btn_subscribe": "💳 Abo",
        "btn_help": "ℹ️ Hilfe", "btn_lang": "🌐 Sprache",
        "btn_crypto_price": "🪙 Preis", "btn_crypto_list": "📋 Liste",
        "btn_crypto_potential": "🔮 Potenzial", "btn_back": "🔙 Zurück",
    },
    "es": {
        "name": "🇪🇸 Español", "choose": "🌐 Seleccione idioma:",
        "lang_set": "Idioma: Español", "sub_expired": "⛔ Suscripción expirada.",
        "wrong_key": "⛔ Clave inválida.",
        "welcome_no_access": "👋 *Market Pulse*\n\nAcceso por suscripción.\n📱 {owner}",
        "welcome_trial": "👋 *¡Hola, {name}!*\n🎁 Prueba: {days} días.",
        "welcome_back": "👋 *¡Bienvenido de nuevo, {name}!*\n💳 Suscripción: *{days}* días\nIdioma: {lang_name}",
        "profile": "👤 ID: `{uid}`\nSuscripción: *{days}* días\nIdioma: {lang_name}\nPropietario: {owner}",
        "price": "*{ticker}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 ¡{ticker} a ${target:.2f}!",
        "no_alerts": "🔔 Sin alertas.",
        "alerts_list": "🔔 *Alertas:*\n\n",
        "del_alert": "✅ {ticker} eliminado",
        "stock_list": "📋 *Acciones:*\n\n",
        "crypto_list": "🪙 *Cripto:*\n\n",
        "gainers": "🚀 *Ganancias:*\n\n",
        "losers": "📉 *Pérdidas:*\n\n",
        "potential": "🔮 *Potencial:*\n\n",
        "crypto_potential": "🔮 *Potencial cripto:*\n\n",
        "news": "📰 *Noticias:*\n\n",
        "no_news": "😴 Sin movimientos.",
        "no_candidates": "🔮 Sin candidatos.",
        "help": "ℹ️ Market Pulse\n\n📊 Precio | 🪙 Cripto | 📈 RSI | 📉 Gráfico\n🔔 Alertas | 👤 Perfil | 🌐 Idioma | 💳 Suscripción",
        "enter_ticker": "Ingrese ticker:",
        "wrong_ticker": "❌ Inválido",
        "use_buttons": "Use menú.",
        "main_menu": "Menú principal",
        "crypto_menu": "🪙 Cripto",
        "searching_news": "📰 Buscando...",
        "backup_ok": "✅ Copia creada.",
        "backup_fail": "❌ Error.",
        "log_empty": "Registro vacío.",
        "no_users": "Sin usuarios.",
        "activated": "✅ {uid} activado {days} días.",
        "notify_activated": "✅ ¡Suscripción extendida {days} días!",
        "users_list": "👥 *Usuarios:*\n\n",
        "subscription_info": "💳 Suscripción: *{days}* días\n\nContacto: {owner}",
        "btn_price": "📊 Precio", "btn_stocks": "📋 Acciones",
        "btn_gainers": "🚀 Ganancias", "btn_losers": "📉 Pérdidas",
        "btn_potential": "🔮 Potencial", "btn_news": "📰 Noticias",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 Gráfico",
        "btn_crypto": "🪙 Cripto", "btn_alerts": "🔔 Alertas",
        "btn_profile": "👤 Perfil", "btn_subscribe": "💳 Suscripción",
        "btn_help": "ℹ️ Ayuda", "btn_lang": "🌐 Idioma",
        "btn_crypto_price": "🪙 Precio", "btn_crypto_list": "📋 Lista",
        "btn_crypto_potential": "🔮 Potencial", "btn_back": "🔙 Volver",
    },
    "it": {
        "name": "🇮🇹 Italiano", "choose": "🌐 Seleziona lingua:",
        "lang_set": "Lingua: Italiano", "sub_expired": "⛔ Abbonamento scaduto.",
        "wrong_key": "⛔ Chiave non valida.",
        "welcome_no_access": "👋 *Market Pulse*\n\nAccesso su abbonamento.\n📱 {owner}",
        "welcome_trial": "👋 *Ciao, {name}!*\n🎁 Prova: {days} giorni.",
        "welcome_back": "👋 *Bentornato, {name}!*\n💳 Abbonamento: *{days}* giorni\nLingua: {lang_name}",
        "profile": "👤 ID: `{uid}`\nAbbonamento: *{days}* giorni\nLingua: {lang_name}\nProprietario: {owner}",
        "price": "*{ticker}*\n💰 ${price:.2f} {emoji} {change:+.2f}%",
        "rsi": "📈 *RSI {ticker}*\n💰 ${price:.2f}\n📊 RSI: *{rsi}* {signal}",
        "chart": "📉 *{ticker}*\n💰 ${price:.2f}\n[📊 TradingView]({link})",
        "alert_set": "🔔 {ticker} a ${target:.2f}!",
        "no_alerts": "🔔 Nessun avviso.",
        "alerts_list": "🔔 *Avvisi:*\n\n",
        "del_alert": "✅ {ticker} rimosso",
        "stock_list": "📋 *Azioni:*\n\n",
        "crypto_list": "🪙 *Cripto:*\n\n",
        "gainers": "🚀 *Migliori:*\n\n",
        "losers": "📉 *Peggiori:*\n\n",
        "potential": "🔮 *Potenziale:*\n\n",
        "crypto_potential": "🔮 *Potenziale cripto:*\n\n",
        "news": "📰 *Notizie:*\n\n",
        "no_news": "😴 Nessun movimento.",
        "no_candidates": "🔮 Nessun candidato.",
        "help": "ℹ️ Market Pulse\n\n📊 Prezzo | 🪙 Cripto | 📈 RSI | 📉 Grafico\n🔔 Avvisi | 👤 Profilo | 🌐 Lingua | 💳 Abbonamento",
        "enter_ticker": "Inserisci ticker:",
        "wrong_ticker": "❌ Non valido",
        "use_buttons": "Usa menu.",
        "main_menu": "Menu principale",
        "crypto_menu": "🪙 Cripto",
        "searching_news": "📰 Ricerca...",
        "backup_ok": "✅ Backup creato.",
        "backup_fail": "❌ Errore.",
        "log_empty": "Log vuoto.",
        "no_users": "Nessun utente.",
        "activated": "✅ {uid} attivato {days} giorni.",
        "notify_activated": "✅ Abbonamento esteso di {days} giorni!",
        "users_list": "👥 *Utenti:*\n\n",
        "subscription_info": "💳 Abbonamento: *{days}* giorni\n\nContatto: {owner}",
        "btn_price": "📊 Prezzo", "btn_stocks": "📋 Azioni",
        "btn_gainers": "🚀 Migliori", "btn_losers": "📉 Peggiori",
        "btn_potential": "🔮 Potenziale", "btn_news": "📰 Notizie",
        "btn_rsi": "📈 RSI", "btn_chart": "📉 Grafico",
        "btn_crypto": "🪙 Cripto", "btn_alerts": "🔔 Avvisi",
        "btn_profile": "👤 Profilo", "btn_subscribe": "💳 Abbonamento",
        "btn_help": "ℹ️ Aiuto", "btn_lang": "🌐 Lingua",
        "btn_crypto_price": "🪙 Prezzo", "btn_crypto_list": "📋 Lista",
        "btn_crypto_potential": "🔮 Potenziale", "btn_back": "🔙 Indietro",
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
    if code and code.startswith("zh"): return LANG["zh"]
    if code and code.startswith("fr"): return LANG["fr"]
    if code and code.startswith("de"): return LANG["de"]
    if code and code.startswith("es"): return LANG["es"]
    if code and code.startswith("it"): return LANG["it"]
    return LANG["en"]

def lang_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh"),
        types.InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
        types.InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"),
        types.InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
        types.InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it"),
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
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params={"range": "5d", "interval": "1d"})
    data = r.json()["chart"]["result"][0]
    prices = data["indicators"]["quote"][0]["close"]
    current = data["meta"]["regularMarketPrice"]
    prev = prices[-2] if len(prices) >= 2 and prices[-2] else current
    return {"price": current, "change": ((current - prev) / prev) * 100 if prev else 0}

def get_crypto_price(symbol):
    data = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}").json()
    current, prev = float(data["lastPrice"]), float(data["openPrice"])
    return {"price": current, "change": ((current - prev) / prev) * 100 if prev else 0}

def get_rsi(ticker, period=14, is_crypto=False):
    if is_crypto:
        data = requests.get(f"https://api.binance.com/api/v3/klines?symbol={ticker}&interval=1d&limit=100").json()
        closes = [float(c[4]) for c in data]
    else:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params={"range": "3mo", "interval": "1d"}).json()
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

def get_news(ticker):
    try:
        data = requests.get(f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}", headers={"User-Agent": "Mozilla/5.0"}).json()
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

# ─── ОБЫЧНЫЕ КОМАНДЫ ────────────────────────────────────
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
        types.KeyboardButton(lang["btn_price"]), types.KeyboardButton(lang["btn_stocks"]),
        types.KeyboardButton(lang["btn_gainers"]), types.KeyboardButton(lang["btn_losers"]),
        types.KeyboardButton(lang["btn_potential"]), types.KeyboardButton(lang["btn_news"]),
        types.KeyboardButton(lang["btn_rsi"]), types.KeyboardButton(lang["btn_chart"]),
        types.KeyboardButton(lang["btn_crypto"]), types.KeyboardButton(lang["btn_alerts"]),
        types.KeyboardButton(lang["btn_profile"]), types.KeyboardButton(lang["btn_subscribe"]),
        types.KeyboardButton(lang["btn_lang"]), types.KeyboardButton(lang["btn_help"])
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

@bot.message_handler(commands=['price'])
def send_price(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    try:
        t = message.text.split()[1].upper()
        d = get_crypto_price(t) if t.endswith("USDT") else get_price(t)
        e = "📈" if d["change"] >= 0 else "📉"
        bot.send_message(message.chat.id, lang["price"].format(ticker=t, price=d["price"], emoji=e, change=d["change"]), parse_mode="Markdown", reply_markup=main_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"])

@bot.message_handler(commands=['rsi'])
def cmd_rsi(message):
    if not is_allowed(message.from_user.id): return
    lang = get_lang(message)
    try:
        t = message.text.split()[1].upper()
        ic = t.endswith("USDT")
        d = get_crypto_price(t) if ic else get_price(t)
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
    if t == lang["btn_price"]:
        msg = bot.reply_to(message, lang["enter_ticker"], reply_markup=types.ForceReply(selective=True))
        bot.register_next_step_handler(msg, lambda m: process_ticker(m, lang))
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
    elif t == lang["btn_back"]: bot.send_message(uid, lang["main_menu"], reply_markup=main_menu(lang))
    elif t == lang["btn_alerts"]: cmd_alerts(message)
    elif t == lang["btn_profile"]: cmd_me(message)
    elif t == lang["btn_subscribe"]: bot.send_message(uid, lang["subscription_info"].format(days=days_left(uid), owner=OWNER_USERNAME), parse_mode="Markdown")
    elif t == lang["btn_help"]: bot.send_message(uid, lang["help"], parse_mode="Markdown", reply_markup=main_menu(lang))
    else:
        try:
            tick = t.upper()
            d = get_crypto_price(tick) if tick.endswith("USDT") else get_price(tick)
            e = "📈" if d["change"]>=0 else "📉"
            bot.send_message(uid, lang["price"].format(ticker=tick, price=d["price"], emoji=e, change=d["change"]), parse_mode="Markdown", reply_markup=main_menu(lang))
        except: bot.reply_to(message, lang["use_buttons"], reply_markup=main_menu(lang))

def process_ticker(message, lang):
    try:
        t = message.text.upper()
        d = get_crypto_price(t) if t.endswith("USDT") else get_price(t)
        e = "📈" if d["change"]>=0 else "📉"
        bot.send_message(message.chat.id, lang["price"].format(ticker=t, price=d["price"], emoji=e, change=d["change"]), parse_mode="Markdown", reply_markup=main_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang))

def process_crypto_ticker(message, lang):
    try:
        t = message.text.upper(); d = get_crypto_price(t)
        e = "📈" if d["change"]>=0 else "📉"
        bot.send_message(message.chat.id, lang["price"].format(ticker=t, price=d["price"], emoji=e, change=d["change"]), parse_mode="Markdown", reply_markup=crypto_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"], reply_markup=crypto_menu(lang))

def process_rsi(message, lang):
    try:
        t = message.text.upper(); ic = t.endswith("USDT")
        d = get_crypto_price(t) if ic else get_price(t)
        r = get_rsi(t, is_crypto=ic)
        s = "🔴" if r>=70 else "🟢" if r<=30 else "⚪" if 40<=r<=60 else "🟠" if r>60 else "🟡"
        bot.send_message(message.chat.id, lang["rsi"].format(ticker=t, price=d["price"], rsi=r, signal=s), parse_mode="Markdown", reply_markup=main_menu(lang))
    except: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang))

def process_chart(message, lang):
    try:
        t = message.text.upper()
        if t.endswith("USDT"): d = get_crypto_price(t); l = get_crypto_chart_link(t)
        else: d = get_price(t); l = get_chart_link(t)
        bot.send_message(message.chat.id, lang["chart"].format(ticker=t, price=d["price"], link=l), parse_mode="Markdown", reply_markup=main_menu(lang), disable_web_page_preview=False)
    except: bot.reply_to(message, lang["wrong_ticker"], reply_markup=main_menu(lang))

def show_watchlist(message, lang):
    text = lang["stock_list"]
    for t in WATCHLIST:
        try:
            d = get_price(t); text += f"• *{t}*: ${d['price']:.2f} {'📈' if d['change']>=0 else '📉'} {d['change']:+.2f}%\n"
        except: text += f"• *{t}*: ❌\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_top_gainers(message, lang):
    dl = []
    for t in WATCHLIST:
        try: d = get_price(t); d["ticker"] = t; dl.append(d)
        except: pass
    dl.sort(key=lambda x: x["change"], reverse=True)
    text = lang["gainers"]
    for i, d in enumerate(dl[:5], 1): text += f"{i}. *{d['ticker']}*: +{d['change']:.2f}%\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_top_losers(message, lang):
    dl = []
    for t in WATCHLIST:
        try: d = get_price(t); d["ticker"] = t; dl.append(d)
        except: pass
    dl.sort(key=lambda x: x["change"])
    text = lang["losers"]
    for i, d in enumerate(dl[:5], 1): text += f"{i}. *{d['ticker']}*: {d['change']:.2f}%\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_potential(message, lang):
    dl = []
    for t in WATCHLIST:
        try: dl.append({"ticker": t, "rsi": get_rsi(t), "price": get_price(t)["price"]})
        except: pass
    dl.sort(key=lambda x: x["rsi"])
    pot = [d for d in dl if d["rsi"] < 45][:5]
    text = (lang["potential"] + "\n".join(f"{'🟢' if d['rsi']<30 else '🟡'} *{d['ticker']}*: RSI {d['rsi']} | ${d['price']:.2f}" for d in pot)) if pot else lang["no_candidates"]
    text += "\n━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(lang))

def show_news_movers(message, lang):
    bot.send_message(message.chat.id, lang["searching_news"])
    mv = []
    for t in WATCHLIST:
        try:
            d = get_price(t)
            if abs(d["change"]) > 1.5: mv.append({"ticker": t, "change": d["change"], "price": d["price"], "news": get_news(t)})
        except: pass
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
        try:
            d = get_crypto_price(t); text += f"• *{t.replace('USDT','')}*: ${d['price']:.2f} {'📈' if d['change']>=0 else '📉'} {d['change']:+.2f}%\n"
        except: text += f"• *{t}*: ❌\n"
    text += "━━━━━━━━━━━━━━━"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=crypto_menu(lang))

def show_crypto_potential(message, lang):
    dl = []
    for t in CRYPTO_LIST:
        try: dl.append({"ticker": t.replace("USDT",""), "rsi": get_rsi(t, is_crypto=True), "price": get_crypto_price(t)["price"]})
        except: pass
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
