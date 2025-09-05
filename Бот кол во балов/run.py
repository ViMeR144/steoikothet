#!/usr/bin/env python3
"""
Скрипт для запуска бота
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def check_environment():
    """Проверка окружения"""
    if not os.getenv('BOT_TOKEN'):
        print("❌ BOT_TOKEN не установлен в .env файле")
        print("Создайте файл .env и добавьте:")
        print("BOT_TOKEN=your_bot_token_here")
        return False
    
    return True

def main():
    """Главная функция"""
    print("🤖 Запуск Stepik Telegram Bot")
    print("=" * 40)
    
    if not check_environment():
        sys.exit(1)
    
    try:
        from bot import StepikBot
        bot = StepikBot()
        print("✅ Бот инициализирован успешно")
        print("🚀 Запуск бота...")
        bot.run()
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()


