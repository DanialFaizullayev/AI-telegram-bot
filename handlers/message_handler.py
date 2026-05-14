from telegram import Update
from telegram.ext import ContextTypes

from ai.chat import ask_groq
from ai.prompts import TOPIC_PROMPTS
from ai.explanations import EXPLAIN_WORDS

from config.settings import (
    user_histories,
    user_topics,
    active_tests
)

from utils.language import detect_language
from utils.markdown import clean_markdown
from utils.keyboards import MAIN_MENU, QUICK_MENU


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    # =========================
    # CHANGE TOPIC
    # =========================

    if message == "🔄 Сменить тему":

        user_topics[user_id] = None
        user_histories[user_id] = []

        await update.message.reply_text(
            "Выбери новый предмет 👇",
            reply_markup=MAIN_MENU
        )

        return

    # =========================
    # TOPIC SELECTION
    # =========================

    if message in TOPIC_PROMPTS:

        user_topics[user_id] = message
        user_histories[user_id] = []

        await update.message.reply_text(
            "✍️ Теперь отправь вопрос или фото задачи.",
            reply_markup=QUICK_MENU
        )

        return

    # =========================
    # NO TOPIC
    # =========================

    if user_topics.get(user_id) is None:

        await update.message.reply_text(
            "📚 Сначала выбери предмет 👇",
            reply_markup=MAIN_MENU
        )

        return

    # =========================
    # TEST ANSWER CHECKING
    # =========================

    if user_id in active_tests and message != "📝 Тест":

        lowered = message.lower()

        # =========================
        # TEST EXPLANATION
        # =========================

        if any(word in lowered for word in EXPLAIN_WORDS):

            test_data = active_tests[user_id]

            explanation_prompt = f"""
Ты преподаватель ЕНТ.

Вот прошлый тест:

{test_data["questions"]}

Правильные ответы:
{test_data["answers"]}

Ответы ученика:
{test_data["user_answers"]}

Объясни КАЖДЫЙ вопрос пошагово.
Объясни почему правильный ответ правильный.
Пиши только на русском языке.
"""

            reply = ask_groq([
                {
                    "role": "system",
                    "content": "Ты helpful ENT tutor."
                },
                {
                    "role": "user",
                    "content": explanation_prompt
                }
            ])

            reply = clean_markdown(reply)

            await update.message.reply_text(
                reply,
                reply_markup=QUICK_MENU
            )

            return

        # =========================
        # CHECK ANSWERS
        # =========================

        raw = message.upper().replace(" ", "")

        raw = (
            raw.replace("А", "A")
               .replace("Б", "B")
               .replace("В", "C")
               .replace("Г", "D")
        )

        user_answers = list(raw)

        test_data = active_tests[user_id]
        correct_answers = test_data["answers"]

        test_data["user_answers"] = user_answers

        score = 0

        result_text = "📊 Результаты теста:\n\n"

        for i, correct in enumerate(correct_answers):

            if i < len(user_answers):

                user_answer = user_answers[i]

                if user_answer == correct:

                    score += 1

                    result_text += (
                        f"{i+1}. ✅ {correct}\n"
                    )

                else:

                    result_text += (
                        f"{i+1}. ❌ {user_answer} | "
                        f"Правильно: {correct}\n"
                    )

            else:

                result_text += (
                    f"{i+1}. ❌ Нет ответа | "
                    f"Правильно: {correct}\n"
                )

        result_text += (
            f"\n🏆 Балл: {score}/{len(correct_answers)}"
        )

        result_text += (
            "\n\n💡 Напиши:\n"
            "'Объясни тест'\n"
            "чтобы получить разбор."
        )

        await update.message.reply_text(
            result_text,
            reply_markup=QUICK_MENU
        )

        return

    # =========================
    # NORMAL CHAT
    # =========================

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({
        "role": "user",
        "content": message
    })

    history = user_histories[user_id][-10:]

    language = detect_language(message)

    system_prompt = (
        TOPIC_PROMPTS[user_topics[user_id]]
        + f"\n\nIMPORTANT: Always answer ONLY in {language} language."
    )

    loading = await update.message.reply_text(
        "⏳ Думаю над ответом...\n"
        "⏳ Жауап дайындап жатырмын..."
    )

    try:

        reply = ask_groq([
            {
                "role": "system",
                "content": system_prompt
            }
        ] + history)

        reply = clean_markdown(reply)

        await loading.delete()

        user_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })

        await update.message.reply_text(
            reply,
            reply_markup=QUICK_MENU
        )

    except Exception as e:

        print(f"Message handler error: {e}")

        await update.message.reply_text(
            "Қате болды, қайта көріңіз / Ошибка, попробуй снова."
        )