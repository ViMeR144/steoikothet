#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from database import Database
import json
from datetime import datetime
import os
import secrets

app = Flask(__name__, template_folder='templates_student')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Инициализация базы данных
db = Database()

# Конфигурация
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

@app.route('/')
def index():
    """Главная страница с выбором роли"""
    if 'user_id' in session:
        user_data = db.get_user(session['user_id'])
        if user_data:
            if user_data['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
    
    return render_template('index.html')

@app.route('/register')
def register():
    """Страница регистрации"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/register_student', methods=['POST'])
def register_student():
    """Регистрация студента"""
    try:
        full_name = request.form.get('full_name', '').strip()
        
        if len(full_name.split()) < 2:
            flash('Пожалуйста, введите полное ФИО (минимум имя и фамилию)', 'error')
            return redirect(url_for('register'))
        
        # Создаем уникальный user_id (в реальном приложении это будет Telegram ID)
        user_id = hash(full_name + str(datetime.now())) % 1000000
        
        # Проверяем, что такой ID не существует
        while db.get_user(user_id):
            user_id = hash(full_name + str(datetime.now()) + str(user_id)) % 1000000
        
        success = db.add_user(
            user_id, 
            full_name.lower().replace(' ', '_'),  # username
            '',  # first_name (будет пустым)
            '',  # last_name (будет пустым)
            'student'
        )
        
        if success:
            db.approve_user(user_id)
            session['user_id'] = user_id
            session['role'] = 'student'
            session['full_name'] = full_name
            flash(f'Регистрация успешна! Добро пожаловать, {full_name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Ошибка регистрации. Попробуйте еще раз.', 'error')
            return redirect(url_for('register'))
            
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('register'))

@app.route('/register_teacher', methods=['POST'])
def register_teacher():
    """Регистрация преподавателя"""
    try:
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        
        if password != ADMIN_PASSWORD:
            flash('Неверный пароль для регистрации преподавателя', 'error')
            return redirect(url_for('register'))
        
        if len(full_name.split()) < 2:
            flash('Пожалуйста, введите полное ФИО (минимум имя и фамилию)', 'error')
            return redirect(url_for('register'))
        
        # Создаем уникальный user_id
        user_id = hash(full_name + str(datetime.now())) % 1000000
        
        # Проверяем, что такой ID не существует
        while db.get_user(user_id):
            user_id = hash(full_name + str(datetime.now()) + str(user_id)) % 1000000
        
        success = db.add_user(
            user_id, 
            full_name.lower().replace(' ', '_'),  # username
            '',  # first_name (будет пустым)
            '',  # last_name (будет пустым)
            'teacher'
        )
        
        if success:
            db.approve_user(user_id)
            session['user_id'] = user_id
            session['role'] = 'teacher'
            session['full_name'] = full_name
            flash(f'Регистрация успешна! Добро пожаловать, {full_name}!', 'success')
            return redirect(url_for('teacher_dashboard'))
        else:
            flash('Ошибка регистрации. Попробуйте еще раз.', 'error')
            return redirect(url_for('register'))
            
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('register'))

@app.route('/student_dashboard')
def student_dashboard():
    """Панель студента"""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    user_data = db.get_user(session['user_id'])
    if not user_data:
        session.clear()
        return redirect(url_for('index'))
    
    # Получаем статистику студента
    student_tests = db.get_student_tests(session['user_id'])
    total_tests = len(student_tests)
    reviewed_tests = len([t for t in student_tests if t['is_reviewed']])
    total_score = sum(t['score'] for t in student_tests if t['is_reviewed'])
    
    return render_template('student_dashboard.html', 
                         user_data=user_data,
                         total_tests=total_tests,
                         reviewed_tests=reviewed_tests,
                         total_score=total_score,
                         tests=student_tests[:5])  # Показываем последние 5 тестов

@app.route('/submit_test', methods=['GET', 'POST'])
def submit_test():
    """Отправка теста"""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Получаем данные формы
            full_name = request.form.get('full_name', '').strip()
            stepik_id = request.form.get('stepik_id', '').strip()
            test_url = request.form.get('test_url', '').strip()
            test_type = request.form.get('test_type', '').strip()
            
            # Валидация
            errors = []
            if not full_name:
                errors.append('ФИО обязательно')
            if not stepik_id:
                errors.append('ID Степика обязателен')
            if not test_url:
                errors.append('Ссылка на тест обязательна')
            if test_type not in ['3', '5']:
                errors.append('Тип теста должен быть 3 или 5')
            
            if errors:
                flash('Ошибки в данных: ' + ', '.join(errors), 'error')
                return render_template('submit_test.html')
            
            # Сохраняем тест
            success = db.add_test(
                session['user_id'],
                full_name,
                stepik_id,
                test_url,
                test_type
            )
            
            if success:
                flash('Тест успешно отправлен! Преподаватель оценит его в ближайшее время.', 'success')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Ошибка при сохранении теста.', 'error')
                
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'error')
    
    return render_template('submit_test.html')

@app.route('/my_results')
def my_results():
    """Результаты студента"""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    user_data = db.get_user(session['user_id'])
    if not user_data:
        session.clear()
        return redirect(url_for('index'))
    
    # Получаем все тесты студента
    student_tests = db.get_student_tests(session['user_id'])
    
    return render_template('my_results.html', 
                         user_data=user_data,
                         tests=student_tests)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    """Панель преподавателя"""
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    user_data = db.get_user(session['user_id'])
    if not user_data:
        session.clear()
        return redirect(url_for('index'))
    
    # Получаем статистику
    stats = db.get_statistics()
    pending_tests = db.get_pending_tests()
    students_scores = db.get_students_scores()
    
    return render_template('teacher_dashboard.html', 
                         user_data=user_data,
                         stats=stats,
                         pending_tests=pending_tests[:5],  # Показываем первые 5
                         students_scores=students_scores[:10])  # Показываем первых 10

@app.route('/pending_tests')
def pending_tests():
    """Страница с неоцененными тестами"""
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    pending_tests = db.get_pending_tests()
    return render_template('pending_tests_teacher.html', tests=pending_tests)

@app.route('/students_list')
def students_list():
    """Список всех студентов"""
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    students_scores = db.get_students_scores()
    return render_template('students_list_teacher.html', students=students_scores)

@app.route('/evaluate_test/<int:test_id>')
def evaluate_test(test_id):
    """Страница оценки теста"""
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    pending_tests = db.get_pending_tests()
    test = next((t for t in pending_tests if t['id'] == test_id), None)
    
    if not test:
        flash('Тест не найден', 'error')
        return redirect(url_for('teacher_dashboard'))
        
    return render_template('evaluate_test_teacher.html', test=test)

@app.route('/submit_evaluation', methods=['POST'])
def submit_evaluation():
    """Обработка оценки теста"""
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    try:
        test_id = int(request.form['test_id'])
        score = int(request.form['score'])
        comment = request.form.get('comment', 'Оценено преподавателем')
        
        success = db.review_test(test_id, score, comment)
        
        if success:
            flash('Тест успешно оценен!', 'success')
            return redirect(url_for('teacher_dashboard'))
        else:
            flash('Ошибка при оценке теста', 'error')
            return redirect(url_for('evaluate_test', test_id=test_id))
            
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('teacher_dashboard'))

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))  # Другой порт, чтобы не конфликтовать с существующим приложением
    app.run(debug=True, host='0.0.0.0', port=port)
