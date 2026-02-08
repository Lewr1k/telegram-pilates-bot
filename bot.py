import os
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# =============================
# Переменные окружения
# =============================
TOKEN = os.getenv("BOT_TOKEN")
ALTEG_API_KEY = os.getenv("ALTEG_API_KEY")
ALTEG_BUSINESS_ID = os.getenv("ALTEG_BUSINESS_ID")

if not TOKEN or not ALTEG_API_KEY or not ALTEG_BUSINESS_ID:
    raise ValueError("❌ Ошибка: BOT_TOKEN, ALTEG_API_KEY или ALTEG_BUSINESS_ID не заданы!")

# =============================
# Хранение chat_id клиентов
# =============================
clients = {}  # {altegio_client_id: chat_id}
sent_reminders = set()  # чтобы не отправлять дубли

# =============================
# Получение всех предстоящих записей из Altegio
# =============================
def get_upcoming_appointments():
    url = f"https://api.alteg.io/v1/appointments?business={ALTEG_BUSINESS_ID}"
    headers = {"Authorization": f"Bearer {ALTEG_API_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("❌ Ошибка API Altegio:", response.text)
        return []

    appointments = response.json().get("data", [])
    now = datetime.now()
    two_hours_later = now + timedelta(hours=2)
    
    # Фильтруем записи, которые начнутся примерно через 2 часа
    upcoming = [
        a for a in appointments
        if two_hours_later - timedelta(minutes=30) <= datetime.fromisoformat(a["start_at"][:-1]) <= two_hours_later + timedelta(minutes=30)
    ]
    return upcoming

# =============================
# Отправка напоминаний
# =============================
async def send_appointment_reminders(app):
    appointments = get_upcoming_appointments()
    for appt in appointments:
        client_id = appt["client"]["id"]
        client_name = appt["client"]["name"]
        chat_id = clients.get(client_id)
        start_time = datetime.fromisoformat(appt["start_at"][:-1]).strftime("%H:%M %d.%m.%Y")

        # уникальный ключ для каждой записи
        reminder_key = f"{client_id}_{appt['id']}"
        if reminder_key in sent_reminders:
            continue  # уже отправлено

        text = f"⏰ Привет, {client_name}! Напоминаем, что ваше занятие начинается через 2 часа: {start_time}."

        if chat_id:
            try:
                await app.bot.send_message(chat_id=chat_id, text=text)
                sent_reminders.add(reminder_key)
                print(f"✅ Напоминание отправлено {client_name}")
            except Exception as e:
                print("❌ Ошибка при отправке:", e)

# =============================
# Команды бота
# =============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    clients.setdefault(chat_id, chat_id)
    
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

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'prices':
        text = "💳 Цены:\n1 занятие — 800₴\nАбонемент на 10 занятий — 7000₴"
    elif query.data == 'Barre':
        text = "❓ Ціни на тренування з Барре:\n- Удобная одежда\n- Запись обязательна"
    elif query.data == 'contacts':
        text = "📍 Адреса: Одесса, вул. Каманина, 16а\n📞 Телефон: +380 99 123 45 67\n🌐 Instagram: https://www.instagram.com/lunara_pilates/"
    elif query.data == 'faq':
        text = "❓ FAQ:\n- Что взять на занятие? Удобную одежду.\n- Можно ли прийти без записи? Нет."
    else:
        text = "❌ Неизвестная опция."

    await query.edit_message_text(text)

# =============================
# Создание приложения
# =============================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

# =============================
# Планировщик
# =============================
scheduler = AsyncIOScheduler()
scheduler.add_job(lambda: send_appointment_reminders(app), 'interval', hours=1)
scheduler.start()

# =============================
# Запуск бота
# =============================
print("Bot started")
app.run_polling()

