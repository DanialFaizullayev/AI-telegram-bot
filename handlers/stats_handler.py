from telegram import Update
from telegram.ext import ContextTypes

from utils.storage import load_users


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()

    await update.message.reply_text(
        f"👥 Всего пользователей: {len(users)}"
    )