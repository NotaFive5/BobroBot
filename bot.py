import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hlink
from aiogram import F, Router
from aiogram.filters import Command
from aiogram import html
from aiogram.utils import executor
from aiogram import Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher
from aiogram import Bot
from aiogram import types
from aiogram.types import BotCommand
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.markdown import hbold, hlink
from aiogram import html

import asyncio

API_TOKEN = 'YOUR_BOT_API_TOKEN'
LEADERBOARD_URL = 'https://serverflappybobr-production.up.railway.app/api/leaderboard'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message(Command(commands=["leaderboard", "top"]))
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
            
            # Ссылка на профиль Telegram по ID
            if username != "Неизвестный":
                leaderboard_text += f'{position}. <a href="tg://user?id={user_id}">{html.escape(username)}</a>: {score}\n'
            else:
                leaderboard_text += f'{position}. {username}: {score}\n'

        await message.reply(leaderboard_text, disable_web_page_preview=True)
    else:
        await message.reply("Не удалось получить таблицу лидеров. Попробуйте позже.")

@dp.message(Command(commands=["start", "help"]))
async def send_welcome(message: Message):
    await message.reply("Привет! Отправь команду /leaderboard или /top, чтобы увидеть таблицу лидеров.")

async def main():
    dp.include_router(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
