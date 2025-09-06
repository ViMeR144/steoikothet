#!/usr/bin/env python3
"""
Скрипт для развертывания бота на хостинге
"""

import os
import sys
import subprocess
import logging

def check_requirements():
    """Проверка требований для развертывания"""
    print("🔍 Проверка требований...")
    
    # Проверяем Python версию
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        return False
    
    # Проверяем наличие файла .env
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден. Создайте его на основе .env.example")
        return False
    
    # Проверяем BOT_TOKEN
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('BOT_TOKEN'):
        print("❌ BOT_TOKEN не установлен в .env файле")
        return False
    
    print("✅ Все требования выполнены")
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("📦 Установка зависимостей...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def test_database():
    """Тестирование базы данных"""
    print("🗄️ Тестирование базы данных...")
    
    try:
        from database import Database
        db = Database()
        print("✅ База данных работает корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_bot():
    """Тестирование бота"""
    print("🤖 Тестирование бота...")
    
    try:
        from bot import StepikBot
        bot = StepikBot()
        print("✅ Бот инициализирован корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации бота: {e}")
        return False

def create_systemd_service():
    """Создание systemd сервиса для Linux"""
    if os.name != 'posix':
        print("⚠️ Systemd сервис доступен только на Linux")
        return True
    
    service_content = f"""[Unit]
Description=Stepik Telegram Bot
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'bot')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} {os.path.join(os.getcwd(), 'bot.py')}
Restart=always
RestartSec=10
Environment=PYTHONPATH={os.getcwd()}

[Install]
WantedBy=multi-user.target
"""
    
    service_file = '/etc/systemd/system/stepik-bot.service'
    
    try:
        with open('stepik-bot.service', 'w') as f:
            f.write(service_content)
        
        print(f"📄 Создан файл сервиса: stepik-bot.service")
        print(f"Для установки выполните:")
        print(f"sudo cp stepik-bot.service {service_file}")
        print(f"sudo systemctl daemon-reload")
        print(f"sudo systemctl enable stepik-bot")
        print(f"sudo systemctl start stepik-bot")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания сервиса: {e}")
        return False

def main():
    """Основная функция развертывания"""
    print("🚀 Развертывание Stepik Telegram Bot")
    print("=" * 40)
    
    steps = [
        ("Проверка требований", check_requirements),
        ("Установка зависимостей", install_dependencies),
        ("Тестирование БД", test_database),
        ("Тестирование бота", test_bot),
        ("Создание сервиса", create_systemd_service)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Развертывание прервано на этапе: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Развертывание завершено успешно!")
    print("\n📝 Следующие шаги:")
    print("1. Убедитесь, что BOT_TOKEN корректный")
    print("2. Запустите бота: python bot.py")
    print("3. Проверьте работу через Telegram")
    print("4. При необходимости настройте автозапуск через systemd")

if __name__ == '__main__':
    main()
