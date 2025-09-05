#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import Database

def check_database():
    """Проверка состояния базы данных"""
    db = Database()
    
    print("=== ПРОВЕРКА БАЗЫ ДАННЫХ ===\n")
    
    # Проверяем пользователей
    print("1. ПОЛЬЗОВАТЕЛИ:")
    try:
        conn = db.db_name
        import sqlite3
        conn = sqlite3.connect(conn)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if users:
            print(f"   Найдено пользователей: {len(users)}")
            for user in users:
                print(f"   - ID: {user[0]}, Имя: {user[1]}, Фамилия: {user[2]}, Роль: {user[3]}, Одобрен: {user[4]}")
        else:
            print("   ❌ Пользователи не найдены!")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Ошибка при проверке пользователей: {e}")
    
    print("\n2. ТЕСТЫ:")
    try:
        conn = sqlite3.connect(db.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tests")
        tests = cursor.fetchall()
        
        if tests:
            print(f"   Найдено тестов: {len(tests)}")
            for test in tests:
                print(f"   - ID: {test[0]}, Студент: {test[1]}, ФИО: {test[2]}, Проверен: {test[7]}, Баллы: {test[8]}")
        else:
            print("   ❌ Тесты не найдены!")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Ошибка при проверке тестов: {e}")
    
    print("\n3. НЕОЦЕНЕННЫЕ ТЕСТЫ:")
    try:
        pending_tests = db.get_pending_tests()
        if pending_tests:
            print(f"   Найдено неоцененных тестов: {len(pending_tests)}")
            for test in pending_tests:
                print(f"   - ID: {test['id']}, Студент: {test['full_name']}, Тип: {test['test_type']}")
        else:
            print("   ❌ Неоцененные тесты не найдены!")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке неоцененных тестов: {e}")
    
    print("\n4. СТУДЕНТЫ С БАЛЛАМИ:")
    try:
        students = db.get_students_scores()
        if students:
            print(f"   Найдено студентов: {len(students)}")
            for student in students:
                print(f"   - ID: {student['user_id']}, Имя: {student['first_name']} {student['last_name']}, Баллы: {student['total_score']}")
        else:
            print("   ❌ Студенты с баллами не найдены!")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке студентов: {e}")

if __name__ == "__main__":
    check_database()
