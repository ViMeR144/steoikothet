#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для подготовки к деплою
"""

import os
import shutil
import secrets

def setup_deployment():
    """Подготовка файлов для деплоя"""
    print("🚀 Подготовка к деплою Stepik Bot...")
    
    # Переименовываем файлы для деплоя
    files_to_rename = [
        ('requirements_deploy.txt', 'requirements.txt'),
        ('Procfile_deploy', 'Procfile'),
        ('runtime_deploy.txt', 'runtime.txt')
    ]
    
    for old_name, new_name in files_to_rename:
        if os.path.exists(old_name):
            if os.path.exists(new_name):
                os.remove(new_name)
            shutil.move(old_name, new_name)
            print(f"✅ {old_name} → {new_name}")
        else:
            print(f"⚠️ Файл {old_name} не найден")
    
    # Создаем .env файл с примером
    env_content = f"""# Переменные окружения для продакшена
SECRET_KEY={secrets.token_hex(32)}
ADMIN_PASSWORD=admin123
BOT_TOKEN=your-telegram-bot-token-here
DEBUG=False
PORT=8000
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Создан .env.example с примером переменных")
    
    # Создаем .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Environment variables
.env

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("✅ Создан .gitignore")
    
    # Создаем README для деплоя
    readme_content = """# Stepik Bot - Telegram Mini App

## 🚀 Быстрый деплой

### Heroku:
1. `heroku create your-app-name`
2. `heroku config:set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"`
3. `heroku config:set ADMIN_PASSWORD="your-password"`
4. `heroku config:set BOT_TOKEN="your-bot-token"`
5. `git push heroku main`

### Railway:
1. Подключите GitHub репозиторий
2. Настройте переменные окружения
3. Деплой автоматический

## 📱 Telegram Mini App URL:
`https://your-domain.com/webapp`

## 🔧 Переменные окружения:
- `SECRET_KEY` - секретный ключ приложения
- `ADMIN_PASSWORD` - пароль для преподавателей
- `BOT_TOKEN` - токен Telegram бота
- `DEBUG` - режим отладки (False для продакшена)

## 📞 Поддержка:
См. файл `ДЕПЛОЙ_НА_СЕРВЕР.md` для подробных инструкций.
"""
    
    with open('README_DEPLOY.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Создан README_DEPLOY.md")
    
    print("\n🎉 Подготовка завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Настройте переменные окружения")
    print("2. Загрузите код на GitHub")
    print("3. Деплойте на выбранную платформу")
    print("4. Настройте Telegram Mini App")
    print("\n📖 Подробные инструкции в файле: ДЕПЛОЙ_НА_СЕРВЕР.md")

if __name__ == '__main__':
    setup_deployment()
