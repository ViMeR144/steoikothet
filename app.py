#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from database import Database
import json
import os
import secrets
import logging

# Настройка логирования для продакшена
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates_student')

# Настройки для продакшена
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'

# Инициализация базы данных
db = Database()

# Конфигурация
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        'message': 'Stepik Bot Web App',
        'status': 'working',
        'version': '1.0.0'
    })

@app.route('/webapp')
def telegram_webapp():
    """Специальная страница для Telegram Mini App"""
    return render_template('telegram_webapp.html')

@app.route('/health')
def health_check():
    """Проверка здоровья приложения"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = app.config['DEBUG']
    
    logger.info(f"Запуск приложения на порту {port}")
    logger.info(f"Debug режим: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)