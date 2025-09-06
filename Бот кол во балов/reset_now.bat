@echo off
chcp 65001 >nul
title Сброс базы данных

echo 🗑️ Принудительный сброс базы данных...
echo.

if exist "stepik_bot.db" (
    del "stepik_bot.db"
    echo ✅ Файл stepik_bot.db удален
) else (
    echo ℹ️ Файл stepik_bot.db не найден
)

echo.
echo 🔄 Создание новой базы данных...

python -c "
import sqlite3
conn = sqlite3.connect('stepik_bot.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        stepik_id TEXT,
        role TEXT CHECK(role IN ('teacher', 'student')),
        is_approved BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        full_name TEXT NOT NULL,
        stepik_id TEXT NOT NULL,
        test_url TEXT NOT NULL,
        test_type TEXT CHECK(test_type IN ('3', '5')),
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_reviewed BOOLEAN DEFAULT FALSE,
        score INTEGER DEFAULT 0,
        teacher_comment TEXT,
        reviewed_at TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users (user_id)
    )
''')

cursor.execute('''
    CREATE TABLE settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
print('✅ Новая база данных создана!')
"

echo.
echo 📊 Проверка базы данных...

python -c "
import sqlite3
conn = sqlite3.connect('stepik_bot.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM users')
users_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM tests')
tests_count = cursor.fetchone()[0]

conn.close()

print(f'📊 Статистика:')
print(f'   • Пользователей: {users_count}')
print(f'   • Тестов: {tests_count}')
print('🎉 База данных полностью сброшена!')
"

echo.
echo 🚀 Теперь можете:
echo    • Обновить страницу в браузере
echo    • Зарегистрироваться заново
echo    • Начать с чистого листа
echo.
pause
