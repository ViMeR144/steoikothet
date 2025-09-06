#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для тестирования веб-приложения локально
"""

import webbrowser
import time
import subprocess
import sys
import os

def install_requirements():
    """Установка зависимостей"""
    print("📦 Устанавливаем зависимости...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask", "gunicorn"])
        print("✅ Зависимости установлены!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка установки зависимостей")
        return False

def start_web_app():
    """Запуск веб-приложения"""
    print("🚀 Запускаем веб-приложение...")
    try:
        # Запускаем Flask приложение
        os.system("python web_app.py")
    except KeyboardInterrupt:
        print("\n⏹️ Приложение остановлено")

def main():
    """Главная функция"""
    print("🎓 Telegram Mini App - Панель преподавателя")
    print("=" * 50)
    
    # Проверяем наличие Flask
    try:
        import flask
        print("✅ Flask уже установлен")
    except ImportError:
        print("❌ Flask не найден")
        if not install_requirements():
            return
    
    print("\n📱 Веб-приложение будет доступно по адресу:")
    print("   http://localhost:5000")
    print("\n🔗 Для Telegram Mini App используйте:")
    print("   https://your-domain.com (после развертывания)")
    
    print("\n⏳ Запускаем через 3 секунды...")
    time.sleep(3)
    
    # Открываем браузер
    webbrowser.open("http://localhost:5000")
    
    # Запускаем приложение
    start_web_app()

if __name__ == "__main__":
    main()

