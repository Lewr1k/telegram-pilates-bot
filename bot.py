import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Получаем токен из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Ошибка: переменная окружения BOT_TOKEN не задана!")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Розклад занять", url="https://n1371162.alteg.io/")],
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

# Обработчик нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # подтверждаем нажатие

    if query.data == 'prices':
        text = "💳 Цены:\n1 занятие — 800₴\nАбонемент на 10 занятий — 7000₴"
    elif query.data == 'Barre':
        text = "❓ Ціни на тренування з Барре:\n- Что взять на занятие? Удобную одежду.\n- Можно ли прийти без записи? Нет, запись обязательна."
    elif query.data == 'contacts':
        text = "📍 Адреса: Одесса, вул. Каманина, 16а\n📞 Телефон: +380 99 123 45 67\n🌐 Instagram: https://www.instagram.com/lunara_pilates/"
    elif query.data == 'faq':
        text = "❓ FAQ:\n- Что взять на занятие? Удобную одежду.\n- Можно ли прийти без записи? Нет, запись обязательна."
    else:
        text = "❌ Неизвестная опция."

    await query.edit_message_text(text)

# Создание приложения
app = ApplicationBuilder().token(TOKEN).build()

# Добавляем обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("Bot started")
app.run_polling()
