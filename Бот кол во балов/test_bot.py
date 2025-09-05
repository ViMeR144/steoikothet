#!/usr/bin/env python3
"""
Тестирование функциональности бота
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_database():
    """Тестирование базы данных"""
    print("🗄️ Тестирование базы данных...")
    
    try:
        from database import Database
        db = Database()
        
        # Тестируем добавление пользователя
        success = db.add_user(12345, "test_user", "Test", "User", "student")
        if success:
            print("✅ Добавление пользователя работает")
        else:
            print("❌ Ошибка добавления пользователя")
            return False
        
        # Тестируем получение пользователя
        user = db.get_user(12345)
        if user and user['role'] == 'student':
            print("✅ Получение пользователя работает")
        else:
            print("❌ Ошибка получения пользователя")
            return False
        
        # Тестируем добавление теста
        success = db.add_test(12345, "Test User", "123456", "https://stepik.org/lesson/123/step/1", "3")
        if success:
            print("✅ Добавление теста работает")
        else:
            print("❌ Ошибка добавления теста")
            return False
        
        # Тестируем получение тестов
        tests = db.get_pending_tests()
        if tests:
            print("✅ Получение тестов работает")
        else:
            print("❌ Ошибка получения тестов")
            return False
        
        # Тестируем статистику
        stats = db.get_statistics()
        if stats:
            print("✅ Получение статистики работает")
        else:
            print("❌ Ошибка получения статистики")
            return False
        
        print("✅ Все тесты базы данных пройдены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования базы данных: {e}")
        return False

def test_utils():
    """Тестирование утилит"""
    print("🔧 Тестирование утилит...")
    
    try:
        from utils import (
            validate_stepik_url, validate_stepik_id, 
            validate_full_name, validate_test_data
        )
        
        # Тестируем валидацию URL
        if validate_stepik_url("https://stepik.org/lesson/123/step/1"):
            print("✅ Валидация URL работает")
        else:
            print("❌ Ошибка валидации URL")
            return False
        
        # Тестируем валидацию ID
        if validate_stepik_id("123456"):
            print("✅ Валидация ID работает")
        else:
            print("❌ Ошибка валидации ID")
            return False
        
        # Тестируем валидацию ФИО
        if validate_full_name("Иванов Иван Иванович"):
            print("✅ Валидация ФИО работает")
        else:
            print("❌ Ошибка валидации ФИО")
            return False
        
        # Тестируем валидацию данных теста
        test_data = {
            'ФИО': 'Иванов Иван Иванович',
            'ID Степика': '123456',
            'Ссылка на тест': 'https://stepik.org/lesson/123/step/1',
            'Тип теста': '3'
        }
        
        validation = validate_test_data(test_data)
        if validation['is_valid']:
            print("✅ Валидация данных теста работает")
        else:
            print("❌ Ошибка валидации данных теста")
            return False
        
        print("✅ Все тесты утилит пройдены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования утилит: {e}")
        return False

def test_feedback():
    """Тестирование системы обратной связи"""
    print("💬 Тестирование системы обратной связи...")
    
    try:
        from database import Database
        from feedback import FeedbackSystem
        
        db = Database()
        feedback_system = FeedbackSystem(db)
        
        # Тестируем отправку отзыва
        success = feedback_system.submit_feedback(12345, 'suggestion', 'Тестовое предложение', 5)
        if success:
            print("✅ Отправка отзыва работает")
        else:
            print("❌ Ошибка отправки отзыва")
            return False
        
        # Тестируем получение статистики отзывов
        stats = feedback_system.get_feedback_stats()
        if stats:
            print("✅ Получение статистики отзывов работает")
        else:
            print("❌ Ошибка получения статистики отзывов")
            return False
        
        # Тестируем отправку уведомления
        success = feedback_system.send_notification(12345, 'Тестовое уведомление', 'info')
        if success:
            print("✅ Отправка уведомления работает")
        else:
            print("❌ Ошибка отправки уведомления")
            return False
        
        print("✅ Все тесты системы обратной связи пройдены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования системы обратной связи: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Тестирование Stepik Telegram Bot")
    print("=" * 40)
    
    tests = [
        ("База данных", test_database),
        ("Утилиты", test_utils),
        ("Система обратной связи", test_feedback)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ Тест {test_name} не пройден")
    
    print(f"\n📊 Результаты тестирования:")
    print(f"✅ Пройдено: {passed}/{total}")
    print(f"❌ Не пройдено: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        return True
    else:
        print("⚠️ Некоторые тесты не пройдены")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


