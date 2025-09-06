#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для миграции базы данных
Добавляет колонку stepik_id в таблицу users
"""

import sqlite3
import os

def migrate_database():
    """Миграция базы данных"""
    db_name = 'stepik_bot.db'
    
    if not os.path.exists(db_name):
        print("❌ База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже колонка stepik_id
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'stepik_id' in columns:
            print("✅ Колонка stepik_id уже существует")
            conn.close()
            return True
        
        print("🔄 Добавляем колонку stepik_id...")
        
        # Добавляем колонку stepik_id
        cursor.execute('''
            ALTER TABLE users ADD COLUMN stepik_id TEXT
        ''')
        
        # Обновляем существующих пользователей
        # Берем stepik_id из их тестов
        cursor.execute('''
            UPDATE users 
            SET stepik_id = (
                SELECT DISTINCT stepik_id 
                FROM tests 
                WHERE tests.student_id = users.user_id 
                LIMIT 1
            )
            WHERE role = 'student'
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Миграция завершена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        return False

if __name__ == "__main__":
    print("🗄️ Миграция базы данных...")
    migrate_database()

