import asyncio
import logging
import psutil
import requests
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from helpers import get_root_disk_usage
from monitoring import check_system_and_sites

# Загрузка переменных окружения из .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")  # Токен бота
WEBSITES = [site.strip().lower() for site in os.getenv('WEBSITES', '').split(',')]

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Бот запущен! Используй /status для проверки состояния.")

@dp.message(Command("status"))
async def check_status(message: Message):
    response_text = "📊 Состояние ресурсов:\n"
    
    # Мониторинг сервера
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    total, used, available, percent = get_root_disk_usage()
    response_text += f"🔹 CPU: {cpu}%\n🔹 RAM: {ram}%\n"
    response_text += f"🔹 Диск: {percent:.2f}% ({available:.2f} свободно из {total:.2f})\n"

    # Мониторинг сайтов
    for site in WEBSITES:
        try:
            response = requests.get(site, timeout=5)
            status = f"✅ {response.status_code}" if response.status_code == 200 else f"⚠️ {response.status_code}"
        except requests.exceptions.RequestException:
            status = "❌ Недоступен"
        response_text += f"{site} - {status}\n"

    await message.answer(response_text)

async def on_startup():
    logging.info("Starting the bot...")
    asyncio.create_task(check_system_and_sites(bot))  # Фоновая задача

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Bot is about to start polling...")
    await on_startup()  # Запуск фонового мониторинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
