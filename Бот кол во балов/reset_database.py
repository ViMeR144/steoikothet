#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для сброса базы данных
"""

import os
import sqlite3

def reset_database():
    """Полный сброс базы данных"""
    db_name = 'stepik_bot.db'
    
    print("🗑️ Сброс базы данных...")
    
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
        CREATE TABLE IF NOT EXISTS users (
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
        CREATE TABLE IF NOT EXISTS tests (
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
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ База данных сброшена и создана заново")
    print("📊 Структура:")
    print("   • Таблица users - пользователи")
    print("   • Таблица tests - тесты")
    print("   • Таблица settings - настройки")
    print("\n🎉 Готово! Можете начинать с чистого листа")

if __name__ == '__main__':
    reset_database()
