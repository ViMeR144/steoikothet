@echo off
chcp 65001 >nul
title Stepik Bot - Запуск всех приложений

echo 🎓 Запуск всех приложений Stepik Bot
echo ================================================
echo.

echo 🚀 Запуск основного веб-приложения (преподаватели)...
start "Основное приложение" cmd /k "python web_app.py"

timeout /t 3 /nobreak >nul

echo 🚀 Запуск студенческого веб-приложения...
start "Студенческое приложение" cmd /k "python start_student_web.py"

timeout /t 3 /nobreak >nul

echo 🚀 Запуск Telegram бота...
start "Telegram Bot" cmd /k "python run.py"

echo.
echo 🎉 Все приложения запущены!
echo.
echo 📱 Доступные ссылки:
echo • Панель преподавателя: http://localhost:5000
echo • Панель студента: http://localhost:5002
echo.
echo 🔧 Для остановки закройте окна приложений
echo.
pause
