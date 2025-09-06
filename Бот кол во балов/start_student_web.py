#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для запуска веб-приложения для студентов
"""

import os
import sys
from student_web_app import app

if __name__ == '__main__':
    print("🚀 Запуск веб-приложения для студентов...")
    print("📱 Доступно по адресу: http://localhost:5002")
    print("🔧 Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)
