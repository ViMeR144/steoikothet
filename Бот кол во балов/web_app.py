#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import Database
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Инициализация базы данных
db = Database()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/students')
def students():
    """Страница со списком студентов"""
    try:
        # Получаем всех студентов с их тестами
        students_data = []
        
        # Получаем всех одобренных студентов
        conn = db.db_name
        import sqlite3
        conn = sqlite3.connect(conn)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.user_id, u.first_name, u.last_name, u.stepik_id,
                   COUNT(t.id) as total_tests,
                   COUNT(CASE WHEN t.is_reviewed = TRUE THEN 1 END) as reviewed_tests,
                   COALESCE(SUM(t.score), 0) as total_score
            FROM users u
            LEFT JOIN tests t ON u.user_id = t.student_id
            WHERE u.role = "student" AND u.is_approved = TRUE
            GROUP BY u.user_id, u.first_name, u.last_name, u.stepik_id
            ORDER BY u.last_name, u.first_name
        ''')
        
        students = cursor.fetchall()
        
        for student in students:
            student_data = {
                'user_id': student[0],
                'first_name': student[1] or '',
                'last_name': student[2] or '',
                'stepik_id': student[3] or '',
                'total_tests': student[4],
                'reviewed_tests': student[5],
                'total_score': student[6],
                'tests': []
            }
            
            # Получаем тесты этого студента
            cursor.execute('''
                SELECT id, full_name, stepik_id, test_url, test_type, 
                       submitted_at, is_reviewed, score, teacher_comment
                FROM tests 
                WHERE student_id = ?
                ORDER BY submitted_at DESC
            ''', (student[0],))
            
            tests = cursor.fetchall()
            for test in tests:
                test_data = {
                    'id': test[0],
                    'full_name': test[1],
                    'stepik_id': test[2],
                    'test_url': test[3],
                    'test_type': test[4],
                    'submitted_at': test[5],
                    'is_reviewed': bool(test[6]),
                    'score': test[7],
                    'teacher_comment': test[8]
                }
                student_data['tests'].append(test_data)
            
            students_data.append(student_data)
        
        conn.close()
        
        return render_template('students.html', students=students_data)
        
    except Exception as e:
        return f"Ошибка: {e}", 500

@app.route('/pending_tests')
def pending_tests():
    """Страница с неоцененными тестами"""
    try:
        pending_tests = db.get_pending_tests()
        return render_template('pending_tests.html', tests=pending_tests)
    except Exception as e:
        return f"Ошибка: {e}", 500

@app.route('/evaluate_test/<int:test_id>')
def evaluate_test(test_id):
    """Страница оценки теста"""
    try:
        tests = db.get_pending_tests()
        test = next((t for t in tests if t['id'] == test_id), None)
        
        if not test:
            return "Тест не найден", 404
            
        return render_template('evaluate_test.html', test=test)
    except Exception as e:
        return f"Ошибка: {e}", 500

@app.route('/submit_evaluation', methods=['POST'])
def submit_evaluation():
    """Обработка оценки теста"""
    try:
        test_id = int(request.form['test_id'])
        score = int(request.form['score'])
        comment = request.form.get('comment', 'Оценено преподавателем')
        
        success = db.review_test(test_id, score, comment)
        
        if success:
            return jsonify({'success': True, 'message': 'Тест успешно оценен!'})
        else:
            return jsonify({'success': False, 'message': 'Ошибка при оценке теста'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {e}'})

@app.route('/student/<int:student_id>')
def student_detail(student_id):
    """Детальная информация о студенте"""
    try:
        # Получаем информацию о студенте
        student_data = db.get_user(student_id)
        if not student_data:
            return "Студент не найден", 404
        
        # Получаем тесты студента
        student_tests = db.get_student_tests(student_id)
        
        return render_template('student_detail.html', 
                             student=student_data, 
                             tests=student_tests)
    except Exception as e:
        return f"Ошибка: {e}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
