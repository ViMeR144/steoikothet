@echo off
echo 🤖 Запуск Stepik Telegram Bot
echo ================================

REM Проверяем наличие файла .env
if not exist .env (
    echo ❌ Файл .env не найден!
    echo Создайте файл .env со следующим содержимым:
    echo BOT_TOKEN=8387916792:AAE-1PbV16QLYX1Xh3X6ssoUt_VgFraPB4w
    echo ADMIN_PASSWORD=admin123
    pause
    exit /b 1
)

REM Устанавливаем зависимости
echo 📦 Установка зависимостей...
pip install -r requirements.txt

REM Запускаем бота
echo 🚀 Запуск бота...
python run.py

pause



