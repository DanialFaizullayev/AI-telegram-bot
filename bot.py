import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

user_histories = {}
user_topics = {}

TOPIC_PROMPTS = {
    "📐 Математика": "You are an expert Math tutor for Kazakh ENT exam. Focus on algebra, geometry, calculus. Give step-by-step solutions.",
    "⚡ Физика": "You are an expert Physics tutor for Kazakh ENT exam. Focus on mechanics, electricity, thermodynamics. Give clear explanations with formulas.",
    "🏛 История Казахстана": "You are an expert on History of Kazakhstan for the ENT exam. Cover ancient history to modern Kazakhstan. Be precise with dates and events.",
    "📚 Общий": "You are a smart study assistant helping Kazakh students prepare for the ENT exam. Help with any subject.",
}

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📐 Математика"), KeyboardButton("⚡ Физика")],
        [KeyboardButton("🏛 История Казахстана"), KeyboardButton("📚 Общий")],
        [KeyboardButton("🔄 Сменить тему")]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    user_topics[user_id] = None
    await update.message.reply_text(
        "Сәлем! Мен ЕНТ дайындығына көмектесетін AI ботпын.\nВыбери предмет для начала:",
        reply_markup=MAIN_MENU
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Как пользоваться ботом:\n\n"
        "1. Выбери предмет из меню\n"
        "2. Задавай любые вопросы\n"
        "3. Нажми 'Сменить тему' чтобы переключиться\n\n"
        "Бот отвечает на казахском, русском и английском языках.",
        reply_markup=MAIN_MENU
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_message == "🔄 Сменить тему":
        user_histories[user_id] = []
        user_topics[user_id] = None
        await update.message.reply_text("Выбери новый предмет:", reply_markup=MAIN_MENU)
        return

    if user_message in TOPIC_PROMPTS:
        user_topics[user_id] = user_message
        user_histories[user_id] = []
        await update.message.reply_text(
            f"Отлично! Ты выбрал {user_message}.\nЗадавай вопросы!",
            reply_markup=MAIN_MENU
        )
        return

    if user_id not in user_topics or user_topics[user_id] is None:
        await update.message.reply_text("Сначала выбери предмет из меню 👇", reply_markup=MAIN_MENU)
        return

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "content": user_message})
    history = user_histories[user_id][-10:]
    system_prompt = TOPIC_PROMPTS[user_topics[user_id]]

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + history
        )
        reply = response.choices[0].message.content
        user_histories[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply, reply_markup=MAIN_MENU)

    except Exception as e:
        await update.message.reply_text("Қате болды, қайта көріңіз / Ошибка, попробуй снова.")
        print(f"Error: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    user_topics[user_id] = None
    await update.message.reply_text("Сброшено! Выбери предмет заново:", reply_markup=MAIN_MENU)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()