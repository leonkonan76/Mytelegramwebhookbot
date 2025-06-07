import os
from flask import Flask, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)
import asyncio

# 🔐 Configuration
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Ex: https://myapp.onrender.com/webhook

main_buttons = ["KF", "BELO", "SOULAN", "KfClone", "Filtres", "Géolocalisation"]
sub_buttons = ["SMS", "CONTACTS", "Historiques appels", "iMessenger", "Facebook Messenger", "Audio", "Vidéo", "Documents", "Autres"]

def get_main_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton(text=btn, callback_data=btn)] for btn in main_buttons])

def get_sub_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton(text=sub, callback_data=sub)] for sub in sub_buttons])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenue dans le bot MyTelegramBot2. Choisissez une option :", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "Géolocalisation":
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("Envoyer ma position", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await query.message.reply_text("Merci de partager votre position :", reply_markup=keyboard)
    elif query.data in main_buttons:
        await query.message.reply_text(f"Vous avez choisi {query.data}. Voici les options disponibles :", reply_markup=get_sub_menu())
    else:
        await query.message.reply_text(f"Vous avez sélectionné : {query.data}")

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        await update.message.reply_text(f"Localisation reçue :\nLatitude: {lat}\nLongitude: {lon}")

# ⚙️ Flask App
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.LOCATION, location_handler))

@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.update_queue.put(update)
    return "ok"

@app.route("/")
def index():
    return "Bot Webhook en ligne."

# Démarrage
async def main():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    asyncio.run(main())