from telegram import Update
from telegram.ext import ContextTypes

from config.settings import active_tests, user_topics
from ai.test_generator import generate_test
from utils.keyboards import QUICK_MENU, MAIN_MENU


async def handle_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    topic = user_topics.get(user_id)

    if topic is None:
        await update.message.reply_text(
            "📚 Сначала выбери предмет 👇",
            reply_markup=MAIN_MENU
        )
        return

    topic_name = topic[2:].strip()



    await update.message.reply_text("⏳ Генерирую тест...")

    reply = generate_test(topic_name)

    if "ANSWERS:" not in reply:
        await update.message.reply_text(reply)
        return

    test_text, answers_text = reply.split("ANSWERS:")

    answers = []

    for line in answers_text.strip().splitlines():
        if "-" in line:
            answers.append(line.split("-")[1].strip().upper())

    active_tests[user_id] = {
        "questions": test_text,
        "answers": answers,
        "user_answers": []
    }

    await update.message.reply_text(
        test_text,
        reply_markup=QUICK_MENU
    )
