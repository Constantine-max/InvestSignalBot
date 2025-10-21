import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "6772849489:AAGFvjhVnjfErkHrn5VlNrytUVXxHE8tMqI"

def get_top_100():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []

async def show_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("📊 Топ-10 криптовалют", callback_data="top10")],
        [InlineKeyboardButton("💰 Топ-50 криптовалют", callback_data="top50")],
        [InlineKeyboardButton("🌍 Топ-100 криптовалют", callback_data="top100")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("👋 Привет! Выбери интересующее 👇", reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.message.reply_text("Выбери интересующее 👇", reply_markup=reply_markup)
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    top_n = 10 if data == "top10" else 50 if data == "top50" else 100

    coins = get_top_100()[:top_n]
    message = f"📈 Топ-{top_n} криптовалют:\n\n"
    for i, coin in enumerate(coins, start=1):
        message += f"{i}. {coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}\n"

    try:
        await query.edit_message_text(message)
    except:
        pass

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))

    print("✅ Бот запущен... Нажми Ctrl+C, чтобы остановить.")
    app.run_polling()

if __name__ == "__main__":
    main()