import os
import threading
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# --- Настройки ---
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_TOKEN не установлена")

CHANNEL_ID = "@perex124"
CHANNEL_LINK = "https://t.me/perex124"
MAIN_BOT_LINK = "https://t.me/Logovoful12bot"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Логика бота (сохраняем вашу оригинальную логику) ---
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return False

def get_sub_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
    ])

@dp.message(CommandStart())
async def cmd_start(message: Message):
    if await is_subscribed(message.from_user.id):
        await message.answer(
            f"Спасибо что поддержали, вот сам бот:\n{MAIN_BOT_LINK}\n\n"
            "(оставайтесь подписаны на канал на всякий случай если бот заблокируют)"
        )
    else:
        await message.answer(
            "Привет это переходник на бот с фуллами он создан для поддержки авторов бота "
            "чтобы пройти дальше подпишитесь на каналы снизу мы не скамеры\n\n"
            f"📢 {CHANNEL_LINK}",
            reply_markup=get_sub_keyboard()
        )

@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.edit_text(
            f"Спасибо что поддержали, вот сам бот:\n{MAIN_BOT_LINK}\n\n"
            "(оставайтесь подписаны на канал на всякий случай если бот заблокируют)"
        )
    else:
        await callback.answer("Вы еще не подписались на канал!", show_alert=True)

# --- Веб-сервер для Render ---
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running"

@app.route("/health")
def health():
    return "OK"

def run_bot():
    """Запуск бота в фоновом потоке"""
    import asyncio
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    # Запуск бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Flask слушает порт, назначенный Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)