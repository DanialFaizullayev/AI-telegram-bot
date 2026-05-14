import base64

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import client, MODEL_NAME, user_topics
from ai.prompts import TOPIC_PROMPTS
from utils.language import detect_language
from utils.markdown import clean_markdown
from utils.keyboards import MAIN_MENU, QUICK_MENU


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_topics.get(user_id) is None:
        await update.message.reply_text(
            "Сначала выбери предмет 👇",
            reply_markup=MAIN_MENU
        )
        return

    await update.message.reply_text("Анализирую вопрос..."
    )

    try:
        photo = update.message.photo[-1]

        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()

        image_data = base64.b64encode(file_bytes).decode("utf-8")

        caption = update.message.caption or ""

        language = detect_language(caption)

        system_prompt = (
            TOPIC_PROMPTS[user_topics[user_id]]
            + f"\n\nIMPORTANT: Always answer ONLY in {language} language."
        )

        response = client.chat.completions.create(model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Реши этот вопрос пошагово."
                        }
                    ]
                }
            ]
        )

        reply = clean_markdown(response.choices[0].message.content)

        await update.message.reply_text(
            reply,
            reply_markup=QUICK_MENU
        )

    except Exception as e:
        print(e)

        await update.message.reply_text(
            "Не удалось обработать изображение."
        )