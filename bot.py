import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = '7799323524:AAF-aYHgq4pTkFjt4Ly20V1FGbmoChZflnY'  
LEADERBOARD_URL = 'https://serverflappybobr-production.up.railway.app/api/leaderboard'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['leaderboard', 'top'])
async def send_leaderboard(message: types.Message):
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
                leaderboard_text += f'{position}. <a href="tg://user?id={user_id}">{username}</a>: {score}\n'
            else:
                leaderboard_text += f'{position}. {username}: {score}\n'

        await message.reply(leaderboard_text, parse_mode="HTML", disable_web_page_preview=True)
    else:
        await message.reply("Не удалось получить таблицу лидеров. Попробуйте позже.")

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь команду /leaderboard или /top, чтобы увидеть таблицу лидеров.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
