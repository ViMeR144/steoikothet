@echo off
chcp 65001 >nul
title Деплой Stepik Bot на Heroku

echo 🚀 Деплой Stepik Bot на Heroku
echo ================================================
echo.

echo 📋 Подготовка файлов...
python deploy_setup.py

echo.
echo 🔧 Настройка Git...
if not exist ".git" (
    git init
    echo ✅ Git репозиторий инициализирован
)

echo.
echo 📝 Добавление файлов в Git...
git add .

echo.
echo 💾 Коммит изменений...
git commit -m "Deploy to Heroku"

echo.
echo 🌐 Создание приложения на Heroku...
echo Введите название вашего приложения:
set /p APP_NAME="Название приложения: "

heroku create %APP_NAME%

echo.
echo ⚙️ Настройка переменных окружения...
heroku config:set SECRET_KEY="%RANDOM%%RANDOM%%RANDOM%%RANDOM%"
heroku config:set ADMIN_PASSWORD="admin123"
heroku config:set BOT_TOKEN="your-telegram-bot-token-here"
heroku config:set DEBUG="False"

echo.
echo 🚀 Деплой на Heroku...
git push heroku main

echo.
echo ✅ Деплой завершен!
echo.
echo 📱 Ваши URL:
echo • Основной сайт: https://%APP_NAME%.herokuapp.com
echo • Telegram Mini App: https://%APP_NAME%.herokuapp.com/webapp
echo.
echo 🔧 Следующие шаги:
echo 1. Обновите BOT_TOKEN в настройках Heroku
echo 2. Настройте Telegram Mini App в @BotFather
echo 3. Протестируйте работу приложения
echo.
echo 📖 Подробные инструкции в файле: ДЕПЛОЙ_НА_СЕРВЕР.md
echo.
pause
