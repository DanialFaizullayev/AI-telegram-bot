from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)

from config.settings import TELEGRAM_TOKEN

from handlers.start_handler import start
from handlers.message_handler import handle_message
from handlers.photo_handler import handle_photo
from handlers.stats_handler import stats
from handlers.test_handler import handle_test

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

app.add_handler(
    MessageHandler(filters.PHOTO, handle_photo)
)

print("Bot is running...")
app.run_polling()