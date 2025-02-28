import logging
import requests
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import os
import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройки
API_TOKEN = os.getenv('API_TOKEN')  # Токен Telegram-бота
SERVER_URL = 'http://localhost:5000'  # URL вашего сервера

if not API_TOKEN:
    raise ValueError("Не найден API_TOKEN! Убедитесь, что переменная окружения настроена правильно.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Клавиатура с кнопкой "Получить реферальную ссылку"
referral_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Получить реферальную ссылку", callback_data="get_referral_link")]
])

# Обработка команды /start
@router.message(Command(commands=["start"]))
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    args = message.text.split()  # Аргументы команды /start

    # Если есть реферальный код
    if len(args) > 1:
        referral_code = args[1]
        try:
            # Отправляем запрос на сервер для регистрации с рефералом
            response = requests.post(f"{SERVER_URL}/api/score", json={
                "username": username,
                "score": 0,  # Начальный счет
                "referredBy": referral_code
            })
            response.raise_for_status()
            await message.reply(f"Вы были приглашены пользователем с кодом {referral_code}!")
        except Exception as e:
            logging.error(f"Ошибка при регистрации с рефералом: {e}")
            await message.reply("Не удалось зарегистрироваться по реферальной ссылке.")
    else:
        # Регистрация без реферала
        try:
            response = requests.post(f"{SERVER_URL}/api/score", json={
                "username": username,
                "score": 0
            })
            response.raise_for_status()
            await message.reply("Добро пожаловать! Используйте /menu для начала.")
        except Exception as e:
            logging.error(f"Ошибка при регистрации: {e}")
            await message.reply("Не удалось зарегистрироваться.")

    # Отправляем клавиатуру с кнопкой для получения реферальной ссылки
    await message.reply("Хотите пригласить друзей?", reply_markup=referral_keyboard)

# Обработка нажатия на кнопку "Получить реферальную ссылку"
@router.callback_query(lambda callback_query: callback_query.data == "get_referral_link")
async def handle_referral_link(callback_query: CallbackQuery):
    username = callback_query.from_user.username
    if not username:
        await callback_query.answer("У вас отсутствует username. Установите его в настройках Telegram.", show_alert=True)
        return

    # Запрос реферальной ссылки у сервера
    try:
        response = requests.get(f"{SERVER_URL}/api/referral_link/{username}")
        response.raise_for_status()
        referral_link = response.json().get("referral_link")
        await callback_query.message.answer(f"Ваша реферальная ссылка: {referral_link}")
    except Exception as e:
        logging.error(f"Ошибка при получении реферальной ссылки: {e}")
        await callback_query.answer("Не удалось получить реферальную ссылку. Попробуйте позже.", show_alert=True)

# Запуск бота
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
