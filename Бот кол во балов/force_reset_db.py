#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

def force_reset_database():
    """Принудительный сброс базы данных"""
    db_name = 'stepik_bot.db'
    
    print("🗑️ Принудительный сброс базы данных...")
    
    # Удаляем старую базу данных
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"✅ Удален файл: {db_name}")
    else:
        print(f"ℹ️ Файл {db_name} не найден")
    
    # Создаем новую базу данных
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Таблица пользователей
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
    
    # Таблица тестов
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
    
    # Таблица настроек
    cursor.execute('''
        CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Новая база данных создана!")
    
    # Проверяем, что база действительно пустая
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    users_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tests')
    tests_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"📊 Проверка:")
    print(f"   • Пользователей: {users_count}")
    print(f"   • Тестов: {tests_count}")
    print("\n🎉 База данных полностью сброшена!")

if __name__ == '__main__':
    force_reset_database()
