import asyncio
import psutil
import requests
import os
from dotenv import load_dotenv
from aiogram import Bot
import logging

from helpers import get_root_disk_usage

# 🔹 Настройки мониторинга
MAX_CPU_USAGE = 95  # Порог загрузки CPU (%)
MAX_RAM_USAGE = 95  # Порог загрузки RAM (%)
MIN_FREE_DISK_GB = 5  # Минимальный порог свободного места на диске (в ГБ)
CHECK_INTERVAL = 3600  # Интервал проверки (секунды)
RECHECK_INTERVAL = 30  # Повторная проверка перед отправкой алерта (секунды)

# 🔹 Загрузка переменных окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

YOUR_USER_ID = os.getenv("USER_ID")
WEBSITES = [site.strip().lower() for site in os.getenv('WEBSITES', '').split(',')]

logging.basicConfig(level=logging.INFO)

async def check_site(site):
    """Проверяет доступность сайта. Возвращает True, если сайт доступен, иначе False."""
    try:
        response = requests.get(site, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

async def check_system_and_sites(bot: Bot):
    site_failures = {}  # Хранит сайты, которые упали в предыдущий раз

    while True:
        try:
            logging.info("Checking system resources...")

            # 🖥️ Проверка системных ресурсов
            cpu_usage = psutil.cpu_percent()
            ram_usage = psutil.virtual_memory().percent
            total, used, available, percent = get_root_disk_usage()

            alert_message = ""

            if cpu_usage > MAX_CPU_USAGE:
                alert_message += f"❗ CPU загружен: {cpu_usage}%\n"
            if ram_usage > MAX_RAM_USAGE:
                alert_message += f"❗ RAM загружена: {ram_usage}%\n"
            if int(available) < MIN_FREE_DISK_GB:
                alert_message += f"❗ Мало места на диске: {available:.2f} ГБ свободно из {total:.2f} ГБ\n"

            # 🌐 Проверка сайтов
            for site in WEBSITES:
                is_down = not await check_site(site)

                if is_down:
                    if site in site_failures:  # Сайт уже был недоступен
                        alert_message += f"❌ {site} недоступен второй раз подряд!\n"
                    else:
                        site_failures[site] = True  # Сайт упал в первый раз
                        logging.warning(f"{site} недоступен. Повторная проверка через {RECHECK_INTERVAL} секунд.")
                        await asyncio.sleep(RECHECK_INTERVAL)
                        if not await check_site(site):  # Повторная проверка
                            alert_message += f"❌ {site} недоступен после повторной проверки!\n"
                        else:
                            site_failures.pop(site, None)  # Сайт восстановился, удаляем его из словаря
                else:
                    if site in site_failures:
                        site_failures.pop(site, None)  # Сайт снова доступен, удаляем его из словаря

            # 📩 Отправка сообщения, если есть алерты
            if alert_message:
                await bot.send_message(YOUR_USER_ID, alert_message)

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logging.error(f"Ошибка при мониторинге: {str(e)}")
            await bot.send_message(YOUR_USER_ID, f"Ошибка при мониторинге: {str(e)}")
