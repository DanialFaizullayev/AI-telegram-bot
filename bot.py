import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

# Memory: stores conversation history per user
user_histories = {}

SYSTEM_PROMPT = """You are a smart study assistant helping Kazakh students prepare for the ENT exam (Unified National Testing). 
You explain topics clearly, give practice questions, and help with Math, Physics, History of Kazakhstan, and other ENT subjects.
Always reply in the same language the user writes in (Kazakh, Russian, or English).
Be encouraging but honest. If a student gets something wrong, correct them kindly."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []  # reset memory on /start
    await update.message.reply_text(
        "Сәлем! Мен ЕНТ дайындығына көмектесетін AI ботпын.\n"
        "Математика, Физика, Қазақстан тарихы — кез келген сұрақ қой!\n\n"
        "Hello! I'm an AI bot for ENT exam prep. Ask me anything!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Initialize history if first message
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Add user message to history
    user_histories[user_id].append({"role": "user", "content": user_message})

    # Keep only last 10 messages to avoid hitting token limits
    history = user_histories[user_id][-10:]

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history
        )

        reply = response.choices[0].message.content

        # Add bot reply to history
        user_histories[user_id].append({"role": "assistant", "content": reply})

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Қате болды, қайта көріңіз / Error occurred, please try again.")
        print(f"Error: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("Сөйлесу тазартылды! / Conversation reset!")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()