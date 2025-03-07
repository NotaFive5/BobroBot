import logging
import requests
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import types
import os
import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Настройки
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
        [KeyboardButton(text="Меню")]
    ],
    resize_keyboard=True,  # Делает клавиатуру компактной
    one_time_keyboard=True,  # Клавиатура остается на экране после нажатия
    input_field_placeholder="KURWA"  # Подсказка в поле ввода
)

# 🚦 **Приветственное сообщение с кнопками (для /start)**
@router.message(Command(commands=["start"]))
async def send_start_message(message: Message):
    # Получаем текст команды (например, "/start ref12345")
    command_args = message.text.split()

    if len(command_args) > 1:
        referral_code = command_args[1]  # Получаем реферальный код
        username = message.from_user.username

        if not username:
            await message.reply("У вас отсутствует username в Telegram. Установите его в настройках Telegram.")
            return

        try:
            # Отправляем запрос на сервер для обработки реферального кода
            response = requests.post(
                f"{SERVER_URL}/api/process_referral",
                json={"username": username, "referral_code": referral_code}
            )
            response.raise_for_status()

            # Получаем ответ от сервера
            data = response.json()
            if data.get("success"):
                await message.reply("Реферальная ссылка успешно применена!")
            else:
                await message.reply(data.get("message", "Не удалось применить реферальную ссылку."))
        except requests.RequestException as e:
            logging.error(f"Ошибка при обработке реферальной ссылки: {e}")
            await message.reply("Не удалось обработать реферальную ссылку. Попробуйте позже.")
    else:
        # Обычное приветственное сообщение
        welcome_text = (
            "🐾 Добро пожаловать в захватывающий мир бобров! 🐾\n\n"
            "🎮 Эта игра создана специально для проекта @BKRVCoin, "
            "чтобы подарить вам увлекательные приключения и незабываемые эмоции!\n\n"
            "💎 Играй, побеждай и зарабатывай! Впереди множество квестов, соревнований "
            "и возможностей получить награды от @BKRVCoin.\n\n"
            "🚀 Начни своё путешествие прямо сейчас! Нажимай кнопку ниже и окунись в удивительный мир бобров!"
        )
        
        await message.reply(
            welcome_text,
            reply_markup=commands_keyboard  # Отображение клавиатуры команд
        )

# 🚦 **Приветственное сообщение с inline-кнопками (для /hi)**
@router.message(lambda message: message.text == "Меню")
async def send_hi(message: Message):
    await message.reply(
        "Ты можешь посмотреть результаты игры здесь:",
        reply_markup=ikb_scoreResult
    )

# 🚦 **Команда /ref для получения реферальной ссылки**
@router.message(Command(commands=["ref"]))
async def send_referral_link(message: Message):
    username = message.from_user.username
    if not username:
        await message.reply("У вас отсутствует username в Telegram. Установите его в настройках Telegram.")
        return

    try:
        # Запрос реферальной ссылки у сервера
        response = requests.get(f"{SERVER_URL}/api/referral_link/{username}")
        
        # Если ссылка не найдена, создаём её
        if response.status_code == 404:
            create_response = requests.post(f"{SERVER_URL}/api/generate_referral", json={"username": username})
            create_response.raise_for_status()
            referral_link = create_response.json().get("referralLink")
        else:
            response.raise_for_status()
            referral_link = response.json().get("referralLink")
        
        if referral_link:
            await message.reply(f"Ваша реферальная ссылка: {referral_link}")
        else:
            await message.reply("Реферальная ссылка не найдена.")
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении реферальной ссылки: {e}")
        await message.reply("Не удалось получить реферальную ссылку. Попробуйте позже.")

# 🚦 **Обработка нажатий на inline-кнопки**
@router.callback_query()
async def handle_callback_query(callback_query: CallbackQuery):
    data = callback_query.data

    if data == "my_score":
        await send_my_score(callback_query.message, callback_query.from_user)
    elif data == "leaderboard_10":
        await send_leaderboard(callback_query.message, limit=10)
    elif data == "leaderboard_20":
        await send_leaderboard(callback_query.message, limit=20)

    await callback_query.answer()

# 🚦 **Вывод лучшего счёта конкретного пользователя**
async def send_my_score(message: Message, user: types.User):
    username = user.username
    if not username:
        await message.reply("У вас отсутствует username в Telegram. Установите его в настройках Telegram.")
        return

    logging.info(f"Запрос очков для пользователя: {username}")

    try:
        response = requests.get(f"{SERVER_URL}/api/user_score/{username}", timeout=10)
        response.raise_for_status()
        data = response.json()
        best_score = data.get("best_score", 0)
        await message.reply(f"Ваш лучший результат: {best_score} очков.")
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе данных пользователя {username}: {e}")
        await message.reply("Не удалось получить ваш лучший результат. Попробуйте позже.")

# 🚦 **Таблица лидеров с динамическим количеством участников**
async def send_leaderboard(message: Message, limit: int = 10):
    logging.info(f"Запрос таблицы лидеров с лимитом: {limit}")

    try:
        response = requests.get(f"{SERVER_URL}/api/leaderboard?limit={limit}", timeout=10)
        response.raise_for_status()
        leaderboard = response.json()
        logging.info(f"Получены данные: {leaderboard}")
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе таблицы лидеров: {e}")
        await message.reply("Не удалось получить таблицу лидеров. Попробуйте позже.")
        return

    if not leaderboard:
        await message.reply("Пока нет данных для таблицы лидеров.")
        return

    leaderboard_text = "🏆 <b>Таблица лидеров:</b>\n\n"
    for index, entry in enumerate(leaderboard, start=1):
        username = entry.get("username", "Неизвестный")
        score = entry.get("score", 0)

        if username != "Неизвестный":
            username_link = f'<a href="https://t.me/{username}">@{username}</a>'
        else:
            username_link = "Неизвестный"

        leaderboard_text += f'{index}. {username_link}: {score}\n'

    await message.reply(leaderboard_text, parse_mode="HTML", disable_web_page_preview=True)

@router.message(Command(commands=["my_referrals"]))
async def check_my_referrals(message: Message):
    username = message.from_user.username
    if not username:
        await message.reply("У вас отсутствует username в Telegram. Установите его в настройках Telegram.")
        return

    try:
        # Запрос количества рефералов у сервера
        response = requests.get(f"{SERVER_URL}/api/my_referrals/{username}", timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            referral_count = data.get("referralCount", 0)
            await message.reply(f"Количество ваших рефералов: {referral_count}")
        else:
            await message.reply(data.get("message", "Не удалось получить количество рефералов."))
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе количества рефералов: {e}")
        await message.reply("Не удалось получить количество рефералов. Попробуйте позже.")

@router.message(Command(commands=["all_referrals"]))
async def check_all_referrals(message: Message):
    try:
        # Запрос общего списка рефералов у сервера
        response = requests.get(f"{SERVER_URL}/api/all_referrals", timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            referral_list = data.get("referralList", [])
            if not referral_list:
                await message.reply("Пока нет данных о рефералах.")
                return

            # Формируем текст для отправки
            referral_text = "🏆 <b>Общий список рефералов:</b>\n\n"
            for entry in referral_list:
                referral_text += f"@{entry['username']}: {entry['referralCount']} рефералов\n"

            await message.reply(referral_text, parse_mode="HTML")
        else:
            await message.reply(data.get("message", "Не удалось получить общий список рефералов."))
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе общего списка рефералов: {e}")
        await message.reply("Не удалось получить общий список рефералов. Попробуйте позже.")

# 🚦 **Запуск бота**
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
