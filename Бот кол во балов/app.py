#!/usr/bin/env python3
"""
Основной файл приложения для развертывания на хостинге
"""

import os
import logging
from bot import StepikBot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Главная функция приложения"""
    # Проверяем наличие токена
    if not os.getenv('BOT_TOKEN'):
        logging.error("BOT_TOKEN не установлен!")
        return
    
    # Создаем и запускаем бота
    bot = StepikBot()
    bot.run()

if __name__ == '__main__':
    main()


