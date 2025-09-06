#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Простой скрипт для запуска веб-приложения
"""

import os
import sys

def main():
    print("🎓 Запуск веб-приложения...")
    print("=" * 40)
    
    # Проверяем наличие Flask
    try:
        import flask
        print("✅ Flask найден")
    except ImportError:
        print("❌ Flask не найден. Устанавливаем...")
        os.system("pip install Flask")
    
    print("\n🚀 Запускаем веб-приложение...")
    print("📱 Откройте в браузере: http://localhost:5000")
    print("⏹️ Для остановки нажмите Ctrl+C")
    print("=" * 40)
    
    # Запускаем веб-приложение
    os.system("python web_app.py")

if __name__ == "__main__":
    main()

