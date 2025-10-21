import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# 🔹 Telegram токен
TOKEN = "6772849489:AAGFvjhVnjfErkHrn5VlNrytUVXxHE8tMqI"

# 🔹 Получение данных по топ-100 криптовалют с CoinGecko
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

# 🔹 Показываем главное меню с кнопками
async def show_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("📊 Топ-10 криптовалют", callback_data="top10")],
        [InlineKeyboardButton("💰 Топ-50 криптовалют", callback_data="top50")],
        [InlineKeyboardButton("🌍 Топ-100 криптовалют", callback_data="top100")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            "👋 Привет! Добро пожаловать в CryptoBot!\nВыбери, что тебе интересно 👇",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        try:
            await update.callback_query.message.reply_text(
                "Выбери, что тебе интересно 👇",
                reply_markup=reply_markup
            )
        except:
            pass

# 🔹 /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)

# 🔹 /help команда
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📌 Команды CryptoBot:\n"
        "/start - показать кнопки с топ криптовалют\n"
        "/help - показать это сообщение\n"
        "/info - информация о боте\n\n"
        "Также можно нажимать кнопки, чтобы видеть топ-10, 50 или 100 криптовалют."
    )
    await update.message.reply_text(text)

# 🔹 /info команда
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 Я CryptoBot!\n"
        "Я могу показывать топ криптовалют по капитализации.\n"
        "Используй кнопки или команды для взаимодействия."
    )
    await update.message.reply_text(text)

# 🔹 Ответ на любые текстовые сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)

# 🔹 Обработка кнопок
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

# 🔹 Основная функция запуска
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))

    print("✅ Бот запущен... Нажми Ctrl+C, чтобы остановить.")
    app.run_polling()

if __name__ == "__main__":
    main()