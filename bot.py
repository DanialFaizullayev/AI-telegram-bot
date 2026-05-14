import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)


import re

def clean_markdown(text):
    # LaTeX math symbols → Unicode
    math_symbols = {
        r'\\alpha': 'α', r'\\beta': 'β', r'\\gamma': 'γ', r'\\delta': 'δ',
        r'\\theta': 'θ', r'\\lambda': 'λ', r'\\mu': 'μ', r'\\pi': 'π',
        r'\\sigma': 'σ', r'\\phi': 'φ', r'\\omega': 'ω', r'\\epsilon': 'ε',
        r'\\infty': '∞', r'\\pm': '±', r'\\leq': '≤', r'\\geq': '≥',
        r'\\neq': '≠', r'\\approx': '≈', r'\\cdot': '·', r'\\times': '×',
        r'\\div': '÷', r'\\sum': 'Σ', r'\\int': '∫', r'\\partial': '∂',
        r'\\sqrt\{(.*?)\}': r'√(\1)', r'\\sqrt': '√',
        r'\\frac\{(.*?)\}\{(.*?)\}': r'\1/\2',
        r'\\sin': 'sin', r'\\cos': 'cos', r'\\tan': 'tan',
        r'\\log': 'log', r'\\ln': 'ln', r'\\lim': 'lim',
        r'\\left': '', r'\\right': '', r'\\quad': ' ', r'\\text\{(.*?)\}': r'\1',
    }
    for pattern, replacement in math_symbols.items():
        text = re.sub(pattern, replacement, text)

    # Remove remaining LaTeX
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'\$+', '', text)
    text = re.sub(r'\\begin\{.*?\}|\\end\{.*?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'(\d)\s*x\s*(\d)', r'\1 * \2', text)
    text = re.sub(r'\{|\}', '', text)
    text = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', text)

        # Superscript numbers
    superscripts = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    def replace_power(match):
        exp = match.group(1)
        if len(exp) == 1 and exp in superscripts:
            return superscripts[exp]
        return '^' + exp
    text = re.sub(r'\^(\w+)', replace_power, text)

    # Long dash for simple fractions like 1/2, d/2
    text = re.sub(r'(\w+)/(\w+)', r'\1÷\2', text)
  
 
    return text.strip()

user_histories = {}
user_topics = {}
import json

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

all_users = load_users()

TOPIC_PROMPTS = {
    "📐 Математика": "You are an expert Math tutor for Kazakh ENT exam. Focus on algebra, geometry, calculus. Give step-by-step solutions. Never use LaTeX or markdown formatting. Write math in plain text only, use ^ for powers and / for fractions.",
    "📖 Грамотность чтения": "You are an expert tutor for Reading Literacy (Грамотность чтения) section of the Kazakh ENT exam. Help students analyze texts, understand main ideas, and answer comprehension questions. Never use LaTeX or markdown formatting.",
    "🏛 История Казахстана": "You are an expert on History of Kazakhstan for the ENT exam. Cover ancient history to modern Kazakhstan. Be precise with dates and events. Never use LaTeX or markdown formatting.",
    "⚡ Физика": "You are an expert Physics tutor for Kazakh ENT exam. Focus on mechanics, electricity, thermodynamics. Give clear explanations with formulas. Never use LaTeX or markdown formatting. Write math in plain text only.",
    "💻 Информатика": "You are an expert Informatics tutor for Kazakh ENT exam. Cover algorithms, data structures, programming basics, computer architecture. For CS terms use English names like Bubble sort, Array, Function rather than literal Kazakh translations. Never use LaTeX or markdown formatting.",    "🧬 Биология": "You are an expert Biology tutor for Kazakh ENT exam. Cover cell biology, genetics, anatomy, ecology. Never use LaTeX or markdown formatting.",
    "⚗️ Химия": "You are an expert Chemistry tutor for Kazakh ENT exam. Cover organic and inorganic chemistry, reactions, periodic table. Never use LaTeX or markdown formatting.",
    "🌍 География": "You are an expert Geography tutor for Kazakh ENT exam. Cover physical and economic geography of Kazakhstan and the world. Never use LaTeX or markdown formatting.",
    "🌐 Всемирная история": "You are an expert World History tutor for Kazakh ENT exam. Cover ancient civilizations to modern history. Be precise with dates and events. Never use LaTeX or markdown formatting.",
    "📚 Общий": "You are a smart study assistant helping Kazakh students prepare for the ENT exam. Help with any subject. Never use LaTeX or markdown formatting.",
}

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📐 Математика"), KeyboardButton("📖 Грамотность чтения")],
        [KeyboardButton("🏛 История Казахстана"), KeyboardButton("⚡ Физика")],
        [KeyboardButton("💻 Информатика"), KeyboardButton("🧬 Биология")],
        [KeyboardButton("⚗️ Химия"), KeyboardButton("🌍 География")],
        [KeyboardButton("🌐 Всемирная история"), KeyboardButton("📚 Общий")],
        [KeyboardButton("🔄 Сменить тему")]
    ],
    resize_keyboard=True
)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_users.add(user_id)
    save_users(all_users)
    user_histories[user_id] = []
    user_topics[user_id] = None
    await update.message.reply_text(
        "Сәлем! 👋 ЕНТ-ге дайындалып жатырсыз ба?\n\n"
        "Привет! Я твой AI помощник для подготовки к ЕНТ 🎯\n"
        "Могу помочь с математикой, историей, физикой и другими предметами.\n\n"
        "Выбери предмет, с которого хочешь начать 👇",
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
    all_users.add(user_id)
    save_users(all_users)
    user_message = update.message.text

    if user_message == "🔄 Сменить тему":
        user_histories[user_id] = []
        user_topics[user_id] = None
        await update.message.reply_text("Выбери новый предмет:", reply_markup=MAIN_MENU)
        return

    if user_message in TOPIC_PROMPTS:
        user_topics[user_id] = user_message
        user_histories[user_id] = []
        topic_intros = {
            "📐 Математика": "алгебра, геометрия, тригонометрия, логарифмы, производные...",
            "📖 Грамотность чтения": "анализ текста, главная мысль, вопросы на понимание...",
            "🏛 История Казахстана": "древняя история, Казахское ханство, советский период, независимость...",
            "⚡ Физика": "механика, электричество, термодинамика, оптика, ядерная физика...",
            "💻 Информатика": "алгоритмы, структуры данных, основы программирования, архитектура ПК...",
            "🧬 Биология": "клетка, генетика, анатомия, экология, эволюция...",
            "⚗️ Химия": "органическая химия, реакции, периодическая таблица, растворы...",
            "🌍 География": "физическая география, экономическая география, Казахстан и мир...",
            "🌐 Всемирная история": "древние цивилизации, средневековье, новое время, XX век...",
            "📚 Общий": "любой предмет ЕНТ...",
        }
        intro = topic_intros.get(user_message, "любые темы...")
        await update.message.reply_text(
            f"Отлично, выбрал {user_message}! Вот что я могу:\n\n"
            f"— Объяснить любую тему ({intro})\n"
            f"— Решить задачу пошагово\n"
            f"— Прислать практические вопросы для тренировки\n"
            f"— Разобрать фото с задачей ЕНТ\n\n"
            f"С чего начнём? Напиши тему или сразу задай вопрос 👇",
            reply_markup=MAIN_MENU
        )
        return

    if user_id not in user_topics or user_topics[user_id] is None:
        
        return

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "content": user_message})
    history = user_histories[user_id][-10:]
    system_prompt = TOPIC_PROMPTS[user_topics[user_id]]

    try:
        response = groq_client.chat.completions.create(
           model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "system", "content": system_prompt}] + history
        )
        reply = response.choices[0].message.content
        reply = clean_markdown(reply)
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


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_topics or user_topics[user_id] is None:
        await update.message.reply_text("Сначала выбери предмет из меню 👇", reply_markup=MAIN_MENU)
        return

    await update.message.reply_text("Анализирую вопрос... / Сұрақты талдап жатырмын...")

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_bytes = await file.download_as_bytearray()

    import base64
    image_data = base64.b64encode(file_bytes).decode("utf-8")

    system_prompt = TOPIC_PROMPTS[user_topics[user_id]]

    try:
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                        {"type": "text", "text": "Реши этот вопрос пошагово. Объясни ответ."}
                    ]
                }
            ]
        )
        reply = response.choices[0].message.content
        reply = clean_markdown(reply)
        await update.message.reply_text(reply, reply_markup=MAIN_MENU)

    except Exception as e:
        await update.message.reply_text("Не удалось обработать изображение. Попробуй снова.")
        print(f"Error: {e}")

    
    all_users = set()

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_users.add(user_id)
    await update.message.reply_text(f"👥 Всего пользователей: {len(all_users)}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(CommandHandler("stats", stats))

print("Bot is running...")
app.run_polling()