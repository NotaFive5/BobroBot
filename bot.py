import logging
import requests
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import html

import os
import asyncio

API_TOKEN = os.getenv('API_TOKEN')  # Получение токена из переменной окружения
LEADERBOARD_URL = 'https://serverflappybobr-production.up.railway.app/api/leaderboard'

if not API_TOKEN:
    raise ValueError("Не найден API_TOKEN! Убедитесь, что переменная окружения настроена правильно.")

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создание отдельного роутера
router = Router()

@router.message(Command(commands=["leaderboard", "top"]))
async def send_leaderboard(message: Message):
    response = requests.get(LEADERBOARD_URL)
    
    if response.status_code == 200:
        leaderboard = response.json()
        if not leaderboard:
            await message.reply("Пока нет данных для таблицы лидеров.")
            return
        
        leaderboard_text = "🏆 <b>Таблица лидеров:</b>\n\n"
        for entry in leaderboard:
            position = entry.get("position", "N/A")
            user_id = entry.get("user_id", "Неизвестный")
            username = entry.get("username", "Неизвестный")
            score = entry.get("score", 0)
            
            if username != "Неизвестный":
                leaderboard_text += f'{position}. <a href="tg://user?id={user_id}">{html.escape(username)}</a>: {score}\n'
            else:
                leaderboard_text += f'{position}. {username}: {score}\n'

        await message.reply(leaderboard_text, parse_mode="HTML", disable_web_page_preview=True)
    else:
        await message.reply("Не удалось получить таблицу лидеров. Попробуйте позже.")

@router.message(Command(commands=["start", "help"]))
async def send_welcome(message: Message):
    await message.reply("Привет! Отправь команду /leaderboard или /top, чтобы увидеть таблицу лидеров.")

async def main():
    dp.include_router(router)  # Подключение роутера к диспетчеру
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
