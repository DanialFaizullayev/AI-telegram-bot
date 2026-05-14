from telegram import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📐 Математика"), KeyboardButton("⚡ Физика")],
        [KeyboardButton("⚗️ Химия"), KeyboardButton("🧬 Биология")],
        [KeyboardButton("💻 Информатика"), KeyboardButton("🌍 География")],
        [KeyboardButton("🏛 История Казахстана"), KeyboardButton("🌐 Всемирная история")],
        [KeyboardButton("📖 Грамотность чтения"), KeyboardButton("📚 Общий")],
        [KeyboardButton("🔄 Сменить тему")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите предмет..."
)

QUICK_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📸 Отправить фото")],
        [KeyboardButton("📝 Тест"), KeyboardButton("📊 Мой прогресс")],
        [KeyboardButton("🔄 Сменить тему")]
    ],
    resize_keyboard=True
)