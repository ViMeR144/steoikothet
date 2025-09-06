#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        'message': 'Stepik Bot Web App - Working!',
        'status': 'healthy',
        'version': '1.0.0'
    })

@app.route('/webapp')
def telegram_webapp():
    """Страница для Telegram Mini App"""
    return jsonify({
        'message': 'Telegram Mini App Page',
        'status': 'ready'
    })

@app.route('/health')
def health_check():
    """Проверка здоровья приложения"""
    return jsonify({
        'status': 'healthy',
        'port': os.environ.get('PORT', '5000')
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
