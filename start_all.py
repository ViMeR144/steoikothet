#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для запуска всех приложений одновременно
"""

import subprocess
import sys
import time
import os
from threading import Thread

def run_web_app():
    """Запуск основного веб-приложения (преподаватели)"""
    try:
        print("🚀 Запуск основного веб-приложения (преподаватели)...")
        subprocess.run([sys.executable, "web_app.py"], check=True)
    except Exception as e:
        print(f"❌ Ошибка запуска основного приложения: {e}")

def run_student_web_app():
    """Запуск студенческого веб-приложения"""
    try:
        print("🚀 Запуск студенческого веб-приложения...")
        subprocess.run([sys.executable, "start_student_web.py"], check=True)
    except Exception as e:
        print(f"❌ Ошибка запуска студенческого приложения: {e}")

def run_bot():
    """Запуск Telegram бота"""
    try:
        print("🚀 Запуск Telegram бота...")
        subprocess.run([sys.executable, "run.py"], check=True)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

if __name__ == '__main__':
    print("🎓 Запуск всех приложений Stepik Bot")
    print("=" * 50)
    
    # Проверяем наличие файлов
    files_to_check = ["web_app.py", "start_student_web.py", "run.py"]
    for file in files_to_check:
        if not os.path.exists(file):
            print(f"❌ Файл {file} не найден!")
            sys.exit(1)
    
    print("✅ Все файлы найдены")
    print("\n📱 Доступные приложения:")
    print("• Основное веб-приложение (преподаватели): http://localhost:5000")
    print("• Студенческое веб-приложение: http://localhost:5002")
    print("• Telegram бот: работает в фоне")
    print("\n🔧 Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        # Запускаем все приложения в отдельных потоках
        threads = []
        
        # Основное веб-приложение
        web_thread = Thread(target=run_web_app, daemon=True)
        web_thread.start()
        threads.append(web_thread)
        
        # Ждем немного перед запуском следующего
        time.sleep(2)
        
        # Студенческое веб-приложение
        student_thread = Thread(target=run_student_web_app, daemon=True)
        student_thread.start()
        threads.append(student_thread)
        
        # Ждем немного перед запуском бота
        time.sleep(2)
        
        # Telegram бот
        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()
        threads.append(bot_thread)
        
        print("\n🎉 Все приложения запущены!")
        print("🌐 Откройте браузер и перейдите по ссылкам выше")
        
        # Ждем завершения
        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print("\n👋 Остановка всех приложений...")
        print("✅ Все приложения остановлены")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
