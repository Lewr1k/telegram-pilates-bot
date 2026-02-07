import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
print("TOKEN:", TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Розклад занятть", url="https://n1371162.alteg.io/")],
        [InlineKeyboardButton("📝 Записатися на заняття", url="https://n1371162.alteg.io/")],
        [InlineKeyboardButton("💳 Ціни на тренування з пілатесу", callback_data='prices')],
        [InlineKeyboardButton("❓ Ціни на тренування з Барре", callback_data='Barre')],
        [InlineKeyboardButton("❓ FAQ", callback_data='faq')],
        [InlineKeyboardButton("📍 Контакты", callback_data='contacts')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в студию пилатеса в Одессе! Выберите опцию:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'prices':
        await query.edit_message_text(
            "💳 Цены:\n1 занятие — 800₴\nАбонемент на 10 занятий — 7000₴"
        )
    elif query.data == 'Barre':
        await query.edit_message_text(
            "❓ Ціни на тренування з Барре:\n"
            "- Что взять на занятие? Удобную одежду.\n"
            "- Можно ли прийти без записи? Нет, запись обязательна."
        )
    elif query.data == 'contacts':
        await query.edit_message_text(
            "📍 Адреса: Одесса, вул. Каманина, 16а\n"
            "📞 Телефон: +380 99 123 45 67\n"
            "🌐 Instagram: https://www.instagram.com/lunara_pilates/"
        )
    elif query.data == 'faq':
        await query.edit_message_text(
            "❓ FAQ:\n"
            "- Что взять на занятие? Удобную одежду.\n"
            "- Можно ли прийти без записи? Нет, запись обязательна."
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CallbackQueryHandler(button))

print("Bot started")
app.run_polling()