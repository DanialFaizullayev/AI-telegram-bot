from telegram import Update
from telegram.ext import ContextTypes

from utils.keyboards import MAIN_MENU
from config.settings import user_histories, user_topics


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_histories[user_id] = []
    user_topics[user_id] = None

    await update.message.reply_text(
        "🎓 AI ЕНТ Assistant\n\n"
        "📚 Подготовка к ЕНТ с AI\n"
        "⚡ Решение задач\n"
        "🧠 Объяснение тем\n"
        "📸 Анализ фото заданий\n\n"
        "Выберите предмет ниже 👇",
        reply_markup=MAIN_MENU
    )