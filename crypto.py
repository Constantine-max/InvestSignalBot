import os

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


def get_top_100():
    """Return the top 100 cryptocurrencies by market capitalization."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


async def show_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("📊 Топ-10 криптовалют", callback_data="top10")],
        [InlineKeyboardButton("💰 Топ-50 криптовалют", callback_data="top50")],
        [InlineKeyboardButton("🌍 Топ-100 криптовалют", callback_data="top100")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            "👋 Привет! Добро пожаловать в CryptoBot!\nВыбери, что тебе интересно 👇",
            reply_markup=reply_markup,
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Выбери, что тебе интересно 👇", reply_markup=reply_markup
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📌 Команды CryptoBot:\n"
        "/start — показать меню\n"
        "/help — показать справку\n"
        "/info — информация о боте"
    )
    await update.message.reply_text(text)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 CryptoBot показывает крупнейшие криптовалюты по рыночной капитализации."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    top_n = {"top10": 10, "top50": 50, "top100": 100}.get(query.data, 10)
    coins = get_top_100()[:top_n]
    if not coins:
        await query.edit_message_text("Не удалось получить данные. Попробуйте позже.")
        return
    lines = [f"📈 Топ-{top_n} криптовалют:", ""]
    for i, coin in enumerate(coins, start=1):
        price = coin["current_price"]
        lines.append(f"{i}. {coin['name']} ({coin['symbol'].upper()}): " + "$" + str(price))
    await query.edit_message_text("\n".join(lines))


def main():
    if not TOKEN:
        raise RuntimeError("Set the TELEGRAM_BOT_TOKEN environment variable before starting the bot")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    print("Бот запущен. Нажмите Ctrl+C, чтобы остановить.")
    app.run_polling()


if __name__ == "__main__":
    main()
