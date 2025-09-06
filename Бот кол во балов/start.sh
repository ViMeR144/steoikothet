#!/bin/bash

echo "🤖 Запуск Stepik Telegram Bot"
echo "================================"

# Проверяем наличие файла .env
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env со следующим содержимым:"
    echo "BOT_TOKEN=8387916792:AAE-1PbV16QLYX1Xh3X6ssoUt_VgFraPB4w"
    echo "ADMIN_PASSWORD=admin123"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install -r requirements.txt

# Запускаем бота
echo "🚀 Запуск бота..."
python run.py



