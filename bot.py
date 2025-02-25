import logging
import requests
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import html
import os
import asyncio

API_TOKEN = os.getenv('API_TOKEN')
SERVER_URL = 'https://serverflappybobr-production.up.railway.app'

if not API_TOKEN:
    raise ValueError("Не найден API_TOKEN! Убедитесь, что переменная окружения настроена правильно.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# 🚦 **Таблица лидеров с динамическим количеством участников**
@router.message(Command(commands=["leaderboard", "top"]))
async def send_leaderboard(message: Message):
    try:
        args = message.text.split()
        limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
        response = requests.get(f"{SERVER_URL}/api/leaderboard?limit={limit}", timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе таблицы лидеров: {e}")
        await message.reply("Не удалось получить таблицу лидеров. Попробуйте позже.")
        return

    leaderboard = response.json()
    if not leaderboard:
        await message.reply("Пока нет данных для таблицы лидеров.")
        return

    leaderboard_text = "🏆 <b>Таблица лидеров:</b>\n\n"
    for entry in leaderboard:
        position = entry.get("position", "N/A")
        username = entry.get("username", "Неизвестный")
        score = entry.get("score", 0)
        leaderboard_text += f'{position}. {html.escape(username)}: {score}\n'

    await message.reply(leaderboard_text, parse_mode="HTML", disable_web_page_preview=True)

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
