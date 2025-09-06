"""
Утилиты для бота
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

def validate_stepik_url(url: str) -> bool:
    """Проверка корректности ссылки на Степик"""
    pattern = r'^https://stepik\.org/(lesson|course|step)/\d+'
    return bool(re.match(pattern, url))

def validate_stepik_id(stepik_id: str) -> bool:
    """Проверка корректности ID Степика"""
    return stepik_id.isdigit() and len(stepik_id) >= 3

def validate_full_name(full_name: str) -> bool:
    """Проверка корректности ФИО"""
    parts = full_name.strip().split()
    return len(parts) >= 2 and all(part.isalpha() for part in parts)

def format_datetime(dt_str: str) -> str:
    """Форматирование даты и времени"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except:
        return dt_str

def calculate_grade_percentage(score: int, max_score: int) -> str:
    """Расчет процентного соотношения оценки"""
    if max_score == 0:
        return "0%"
    
    percentage = (score / max_score) * 100
    if percentage >= 90:
        return f"{percentage:.1f}% (Отлично)"
    elif percentage >= 80:
        return f"{percentage:.1f}% (Хорошо)"
    elif percentage >= 70:
        return f"{percentage:.1f}% (Удовлетворительно)"
    else:
        return f"{percentage:.1f}% (Неудовлетворительно)"

def get_emoji_for_score(score: int, max_score: int) -> str:
    """Получение эмодзи для оценки"""
    if max_score == 0:
        return "❌"
    
    percentage = (score / max_score) * 100
    if percentage >= 90:
        return "🌟"
    elif percentage >= 80:
        return "✅"
    elif percentage >= 70:
        return "👍"
    elif percentage >= 50:
        return "⚠️"
    else:
        return "❌"

def format_test_submission_guide() -> str:
    """Форматированная инструкция по отправке теста"""
    return """
📤 <b>Как отправить тест:</b>

Отправьте сообщение в следующем формате:

<code>ФИО: Иванов Иван Иванович
ID Степика: 123456
Ссылка на тест: https://stepik.org/lesson/123456/step/1
Тип теста: 3</code>

<b>Требования:</b>
• ФИО: минимум имя и фамилия
• ID Степика: числовой идентификатор
• Ссылка: должна быть с stepik.org
• Тип теста: 3 или 5 баллов

<b>Примеры ссылок:</b>
• https://stepik.org/lesson/123456/step/1
• https://stepik.org/course/789012/step/2
"""

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Создание прогресс-бара"""
    if total == 0:
        return "░" * length
    
    filled = int((current / total) * length)
    bar = "█" * filled + "░" * (length - filled)
    percentage = (current / total) * 100
    
    return f"{bar} {percentage:.1f}%"

def get_time_ago(dt_str: str) -> str:
    """Получение времени в формате 'X назад'"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} дн. назад"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ч. назад"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} мин. назад"
        else:
            return "только что"
    except:
        return "неизвестно"

def validate_test_data(data: Dict[str, str]) -> Dict[str, str]:
    """Валидация данных теста"""
    errors = []
    
    # Проверка ФИО
    if 'ФИО' not in data or not validate_full_name(data['ФИО']):
        errors.append("Некорректное ФИО")
    
    # Проверка ID Степика
    if 'ID Степика' not in data or not validate_stepik_id(data['ID Степика']):
        errors.append("Некорректный ID Степика")
    
    # Проверка ссылки
    if 'Ссылка на тест' not in data or not validate_stepik_url(data['Ссылка на тест']):
        errors.append("Некорректная ссылка на тест")
    
    # Проверка типа теста
    if 'Тип теста' not in data or data['Тип теста'] not in ['3', '5']:
        errors.append("Тип теста должен быть 3 или 5")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def format_statistics_summary(stats: Dict) -> str:
    """Форматирование сводки статистики"""
    total_tests = stats.get('total_tests', 0)
    reviewed_tests = stats.get('reviewed_tests', 0)
    pending_tests = stats.get('pending_tests', 0)
    avg_score = stats.get('average_score', 0)
    
    progress_bar = create_progress_bar(reviewed_tests, total_tests)
    
    return f"""
📊 <b>Сводка статистики</b>

👥 Студентов: {stats.get('total_students', 0)}
📝 Всего тестов: {total_tests}
✅ Оценено: {reviewed_tests}
⏳ Ожидает: {pending_tests}

📈 Прогресс: {progress_bar}
📊 Средний балл: {avg_score}

{get_emoji_for_score(avg_score, 5)} Общая оценка: {calculate_grade_percentage(avg_score, 5)}
"""

def generate_feedback_message(score: int, max_score: int, comment: str = "") -> str:
    """Генерация сообщения с обратной связью"""
    emoji = get_emoji_for_score(score, max_score)
    percentage = calculate_grade_percentage(score, max_score)
    
    message = f"{emoji} <b>Ваша оценка: {score}/{max_score}</b>\n"
    message += f"📊 {percentage}\n"
    
    if comment:
        message += f"\n💬 <b>Комментарий преподавателя:</b>\n{comment}"
    
    # Добавляем мотивационные сообщения
    if score == max_score:
        message += "\n\n🎉 Отличная работа! Продолжайте в том же духе!"
    elif score >= max_score * 0.8:
        message += "\n\n👍 Хорошая работа! Есть небольшие недочеты."
    elif score >= max_score * 0.6:
        message += "\n\n📚 Неплохо, но есть над чем поработать."
    else:
        message += "\n\n💪 Не расстраивайтесь! Изучите материал еще раз и попробуйте снова."
    
    return message



