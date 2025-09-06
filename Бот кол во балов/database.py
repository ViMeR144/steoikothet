import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_name: str = 'stepik_bot.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                stepik_id TEXT,
                role TEXT CHECK(role IN ('teacher', 'student')),
                is_approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица тестов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                full_name TEXT NOT NULL,
                stepik_id TEXT NOT NULL,
                test_url TEXT NOT NULL,
                test_type TEXT CHECK(test_type IN ('3', '5')),
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_reviewed BOOLEAN DEFAULT FALSE,
                score INTEGER DEFAULT 0,
                teacher_comment TEXT,
                reviewed_at TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица настроек
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("База данных инициализирована")
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str, role: str) -> bool:
        """Добавление пользователя"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, role))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления пользователя: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получение пользователя по ID"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'first_name': user[2],
                    'last_name': user[3],
                    'role': user[4],
                    'is_approved': bool(user[5]),
                    'created_at': user[6]
                }
            return None
        except Exception as e:
            logging.error(f"Ошибка получения пользователя: {e}")
            return None
    
    def approve_user(self, user_id: int) -> bool:
        """Одобрение пользователя"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET is_approved = TRUE WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка одобрения пользователя: {e}")
            return False
    
    def add_test(self, student_id: int, full_name: str, stepik_id: str, test_url: str, test_type: str) -> bool:
        """Добавление теста"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tests (student_id, full_name, stepik_id, test_url, test_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, full_name, stepik_id, test_url, test_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления теста: {e}")
            return False
    
    def get_pending_tests(self) -> List[Dict]:
        """Получение неоцененных тестов"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.*, u.username, u.first_name, u.last_name
                FROM tests t
                JOIN users u ON t.student_id = u.user_id
                WHERE t.is_reviewed = FALSE
                ORDER BY t.submitted_at DESC
            ''')
            
            tests = cursor.fetchall()
            conn.close()
            
            return [{
                'id': test[0],
                'student_id': test[1],
                'full_name': test[2],
                'stepik_id': test[3],
                'test_url': test[4],
                'test_type': test[5],
                'submitted_at': test[6],
                'username': test[8],
                'first_name': test[9],
                'last_name': test[10]
            } for test in tests]
        except Exception as e:
            logging.error(f"Ошибка получения тестов: {e}")
            return []
    
    def review_test(self, test_id: int, score: int, comment: str = "") -> bool:
        """Оценка теста"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tests 
                SET is_reviewed = TRUE, score = ?, teacher_comment = ?, reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (score, comment, test_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка оценки теста: {e}")
            return False
    
    def get_student_tests(self, student_id: int) -> List[Dict]:
        """Получение тестов студента"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM tests 
                WHERE student_id = ? 
                ORDER BY submitted_at DESC
            ''', (student_id,))
            
            tests = cursor.fetchall()
            conn.close()
            
            return [{
                'id': test[0],
                'student_id': test[1],
                'full_name': test[2],
                'stepik_id': test[3],
                'test_url': test[4],
                'test_type': test[5],
                'submitted_at': test[6],
                'is_reviewed': bool(test[7]),
                'score': test[8],
                'teacher_comment': test[9],
                'reviewed_at': test[10]
            } for test in tests]
        except Exception as e:
            logging.error(f"Ошибка получения тестов студента: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Общее количество студентов
            cursor.execute('SELECT COUNT(*) FROM users WHERE role = "student" AND is_approved = TRUE')
            total_students = cursor.fetchone()[0] or 0
            
            # Общее количество тестов
            cursor.execute('SELECT COUNT(*) FROM tests')
            total_tests = cursor.fetchone()[0] or 0
            
            # Оцененные тесты
            cursor.execute('SELECT COUNT(*) FROM tests WHERE is_reviewed = TRUE')
            reviewed_tests = cursor.fetchone()[0] or 0
            
            # Средний балл
            cursor.execute('SELECT AVG(score) FROM tests WHERE is_reviewed = TRUE')
            avg_score = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_students': total_students,
                'total_tests': total_tests,
                'reviewed_tests': reviewed_tests,
                'pending_tests': total_tests - reviewed_tests,
                'average_score': round(avg_score, 2)
            }
        except Exception as e:
            logging.error(f"Ошибка получения статистики: {e}")
            return {
                'total_students': 0,
                'total_tests': 0,
                'reviewed_tests': 0,
                'pending_tests': 0,
                'average_score': 0
            }
    
    def get_students_scores(self) -> List[Dict]:
        """Получение баллов всех студентов"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.user_id, 
                       COALESCE(MAX(t.full_name), 'Не указано') as full_name,
                       COALESCE(SUM(t.score), 0) as total_score,
                       COUNT(t.id) as total_tests,
                       COUNT(CASE WHEN t.is_reviewed = TRUE THEN 1 END) as reviewed_tests
                FROM users u
                LEFT JOIN tests t ON u.user_id = t.student_id
                WHERE u.role = "student" AND u.is_approved = TRUE
                GROUP BY u.user_id
                ORDER BY total_score DESC
            ''')
            
            students = cursor.fetchall()
            conn.close()
            
            return [{
                'user_id': student[0],
                'full_name': student[1] or 'Не указано',
                'stepik_id': '',  # Будет заполнено из тестов
                'total_score': student[2],
                'total_tests': student[3],
                'reviewed_tests': student[4]
            } for student in students]
        except Exception as e:
            logging.error(f"Ошибка получения баллов студентов: {e}")
            return []

