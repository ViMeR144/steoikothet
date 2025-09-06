#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для проверки статуса всех приложений
"""

import requests
import subprocess
import sys
import os

def check_port(port):
    """Проверка доступности порта"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=5)
        return True, response.status_code
    except requests.exceptions.RequestException:
        return False, None

def check_process(process_name):
    """Проверка запущенного процесса"""
    try:
        result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}'], 
                              capture_output=True, text=True, shell=True)
        return process_name in result.stdout
    except:
        return False

def main():
    print("🔍 Проверка статуса приложений Stepik Bot")
    print("=" * 50)
    
    # Проверяем порты
    print("📡 Проверка веб-приложений:")
    
    # Основное приложение (преподаватели)
    is_running_5000, status_5000 = check_port(5000)
    if is_running_5000:
        print(f"✅ Основное приложение (порт 5000): Работает (статус: {status_5000})")
        print(f"   🌐 http://localhost:5000")
    else:
        print("❌ Основное приложение (порт 5000): Не работает")
    
    # Студенческое приложение
    is_running_5002, status_5002 = check_port(5002)
    if is_running_5002:
        print(f"✅ Студенческое приложение (порт 5002): Работает (статус: {status_5002})")
        print(f"   🌐 http://localhost:5002")
    else:
        print("❌ Студенческое приложение (порт 5002): Не работает")
    
    print("\n🤖 Проверка процессов Python:")
    
    # Проверяем процессы Python
    python_processes = check_process('python.exe')
    if python_processes:
        print("✅ Процессы Python: Запущены")
    else:
        print("❌ Процессы Python: Не найдены")
    
    print("\n📋 Рекомендации:")
    
    if not is_running_5000 and not is_running_5002:
        print("🔧 Запустите приложения:")
        print("   python start_all.py")
    elif not is_running_5000:
        print("🔧 Запустите основное приложение:")
        print("   python web_app.py")
    elif not is_running_5002:
        print("🔧 Запустите студенческое приложение:")
        print("   python start_student_web.py")
    else:
        print("🎉 Все приложения работают корректно!")
    
    print("\n📱 Доступные ссылки:")
    if is_running_5000:
        print(f"   👨‍🏫 Панель преподавателя: http://localhost:5000")
    if is_running_5002:
        print(f"   👨‍🎓 Панель студента: http://localhost:5002")

if __name__ == '__main__':
    main()
