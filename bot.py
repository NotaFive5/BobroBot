import logging
import requests
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import os
import asyncio
import html as std_html
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv('API_TOKEN')  # Токен Telegram-бота
SERVER_URL = 'https://serverflappybobr-production.up.railway.app'  # Публичный URL сервера

if not API_TOKEN:
    raise ValueError("Не найден API_TOKEN! Убедитесь, что переменная окружения настроена правильно.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# 🚦 **Создание inline-клавиатуры**
ikb_scoreResult = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мои очки', callback_data="my_score")],
    [InlineKeyboardButton(text='Топ 10', callback_data="leaderboard_10")],
    [InlineKeyboardButton(text='Топ 20', callback_data="leaderboard_20")]
])

# 🚦 **Создание клавиатуры команд рядом с полем ввода**
commands_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/hi")]
    ],
    resize_keyboard=True,  # Делает клавиатуру компактной
    one_time_keyboard=True,  # Клавиатура остается на экране после нажатия
    input_field_placeholder="KURWA"
# 🚦 **Приветственное сообщение с кнопками**
@router.message(Command(commands=["start", "help"]))
async def send_welcome(message: Message):
    await message.reply(
        "Ты можешь посмотреть результаты игры здесь:",
        reply_markup=commands_keyboard  # Отображение клавиатуры команд
        
# 🚦 **Приветственное сообщение с кнопками**
@router.message(Command(commands=["hi", "start", "help"]))
async def send_welcome(message: Message):
    await message.reply(
        "Ты можешь посмотреть результаты игры здесь:",
        reply_markup=ikb_scoreResult
    )

# 🚦 **Обработка нажатий на inline-кнопки**
@router.callback_query()
async def handle_callback_query(callback_query: CallbackQuery):
    data = callback_query.data

    if data == "my_score":
        await send_my_score(callback_query.message)
    elif data == "leaderboard_10":
        await send_leaderboard(callback_query.message, limit=10)
    elif data == "leaderboard_20":
        await send_leaderboard(callback_query.message, limit=20)

    await callback_query.answer()

# 🚦 **Таблица лидеров с динамическим количеством участников**
async def send_leaderboard(message: Message, limit: int = 10):
    logging.info("Команда /leaderboard получена")

    try:
        response = requests.get(f"{SERVER_URL}/api/leaderboard?limit={limit}", timeout=10)
        response.raise_for_status()
        logging.info("Данные успешно получены от сервера")
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе таблицы лидеров: {e}")
        await message.reply("Не удалось получить таблицу лидеров. Попробуйте позже.")
        return

    leaderboard = response.json()
    logging.info(f"Получены данные: {leaderboard}")

    if not leaderboard:
        await message.reply("Пока нет данных для таблицы лидеров.")
        return

    leaderboard_text = "🏆 <b>Таблица лидеров:</b>\n\n"
    for index, entry in enumerate(leaderboard, start=1):
        username = entry.get("username", "Неизвестный")
        score = entry.get("score", 0)

        # Если username существует, делаем его кликабельным, иначе выводим текст "Неизвестный"
        if username != "Неизвестный":
            username_link = f'<a href="https://t.me/{std_html.escape(username)}">@{std_html.escape(username)}</a>'
        else:
            username_link = "Неизвестный"

        leaderboard_text += f'{index}. {username_link}: {score}\n'

    logging.info(f"Подготовленный текст для отправки:\n{leaderboard_text}")

    try:
        await message.reply(leaderboard_text, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("Сообщение отправлено успешно.")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в Telegram: {e}")

# 🚦 **Вывод лучшего счёта конкретного пользователя**
async def send_my_score(message: Message):
    username = message.from_user.username
    if not username:
        await message.reply("У вас отсутствует username в Telegram. Установите его в настройках Telegram.")
        return

    try:
        response = requests.get(f"{SERVER_URL}/api/user_score/{username}", timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе данных пользователя {username}: {e}")
        await message.reply("Не удалось получить ваш лучший результат. Попробуйте позже.")
        return

    data = response.json()
    best_score = data.get("best_score", 0)
    await message.reply(f"Ваш лучший результат: {best_score} очков.")

# 🚦 **Запуск бота**
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) нужно чтобы hi была в той клавиатуре
