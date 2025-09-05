"""
Модуль обратной связи для бота
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from database import Database

class FeedbackSystem:
    def __init__(self, db: Database):
        self.db = db
        self.setup_feedback_tables()
    
    def setup_feedback_tables(self):
        """Создание таблиц для системы обратной связи"""
        conn = self.db.db_name
        import sqlite3
        
        with sqlite3.connect(conn) as connection:
            cursor = connection.cursor()
            
            # Таблица отзывов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    feedback_type TEXT CHECK(feedback_type IN ('bug', 'suggestion', 'compliment', 'question')),
                    message TEXT NOT NULL,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    is_processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица уведомлений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT NOT NULL,
                    notification_type TEXT CHECK(notification_type IN ('info', 'warning', 'success', 'error')),
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            connection.commit()
    
    def submit_feedback(self, user_id: int, feedback_type: str, message: str, rating: Optional[int] = None) -> bool:
        """Отправка отзыва"""
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_name) as connection:
                cursor = connection.cursor()
                
                cursor.execute('''
                    INSERT INTO feedback (user_id, feedback_type, message, rating)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, feedback_type, message, rating))
                
                connection.commit()
                return True
        except Exception as e:
            logging.error(f"Ошибка отправки отзыва: {e}")
            return False
    
    def get_feedback_stats(self) -> Dict:
        """Получение статистики отзывов"""
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_name) as connection:
                cursor = connection.cursor()
                
                # Общее количество отзывов
                cursor.execute('SELECT COUNT(*) FROM feedback')
                total_feedback = cursor.fetchone()[0]
                
                # Отзывы по типам
                cursor.execute('''
                    SELECT feedback_type, COUNT(*) 
                    FROM feedback 
                    GROUP BY feedback_type
                ''')
                feedback_by_type = dict(cursor.fetchall())
                
                # Средний рейтинг
                cursor.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
                avg_rating = cursor.fetchone()[0] or 0
                
                # Необработанные отзывы
                cursor.execute('SELECT COUNT(*) FROM feedback WHERE is_processed = FALSE')
                unprocessed = cursor.fetchone()[0]
                
                return {
                    'total_feedback': total_feedback,
                    'feedback_by_type': feedback_by_type,
                    'average_rating': round(avg_rating, 2),
                    'unprocessed_feedback': unprocessed
                }
        except Exception as e:
            logging.error(f"Ошибка получения статистики отзывов: {e}")
            return {}
    
    def send_notification(self, user_id: int, message: str, notification_type: str = 'info') -> bool:
        """Отправка уведомления пользователю"""
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_name) as connection:
                cursor = connection.cursor()
                
                cursor.execute('''
                    INSERT INTO notifications (user_id, message, notification_type)
                    VALUES (?, ?, ?)
                ''', (user_id, message, notification_type))
                
                connection.commit()
                return True
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления: {e}")
            return False
    
    def get_user_notifications(self, user_id: int, unread_only: bool = True) -> List[Dict]:
        """Получение уведомлений пользователя"""
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_name) as connection:
                cursor = connection.cursor()
                
                query = 'SELECT * FROM notifications WHERE user_id = ?'
                params = [user_id]
                
                if unread_only:
                    query += ' AND is_read = FALSE'
                
                query += ' ORDER BY created_at DESC LIMIT 10'
                
                cursor.execute(query, params)
                notifications = cursor.fetchall()
                
                return [{
                    'id': notif[0],
                    'user_id': notif[1],
                    'message': notif[2],
                    'notification_type': notif[3],
                    'is_read': bool(notif[4]),
                    'created_at': notif[5]
                } for notif in notifications]
        except Exception as e:
            logging.error(f"Ошибка получения уведомлений: {e}")
            return []
    
    def mark_notification_read(self, notification_id: int) -> bool:
        """Отметка уведомления как прочитанного"""
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_name) as connection:
                cursor = connection.cursor()
                
                cursor.execute('''
                    UPDATE notifications 
                    SET is_read = TRUE 
                    WHERE id = ?
                ''', (notification_id,))
                
                connection.commit()
                return True
        except Exception as e:
            logging.error(f"Ошибка отметки уведомления: {e}")
            return False
    
    def get_feedback_form_keyboard(self):
        """Клавиатура для формы обратной связи"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("🐛 Сообщить об ошибке", callback_data="feedback_bug")],
            [InlineKeyboardButton("💡 Предложение", callback_data="feedback_suggestion")],
            [InlineKeyboardButton("👍 Похвалить", callback_data="feedback_compliment")],
            [InlineKeyboardButton("❓ Задать вопрос", callback_data="feedback_question")],
            [InlineKeyboardButton("📊 Оценить бота", callback_data="feedback_rating")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_rating_keyboard(self):
        """Клавиатура для оценки бота"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("⭐ 1", callback_data="rating_1"),
             InlineKeyboardButton("⭐⭐ 2", callback_data="rating_2"),
             InlineKeyboardButton("⭐⭐⭐ 3", callback_data="rating_3")],
            [InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data="rating_4"),
             InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data="rating_5")]
        ]
        return InlineKeyboardMarkup(keyboard)


