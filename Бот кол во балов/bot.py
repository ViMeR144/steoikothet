import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)
from database import Database
from config import BOT_TOKEN, ADMIN_PASSWORD
from utils import (
    validate_test_data, format_statistics_summary, 
    generate_feedback_message, format_test_submission_guide
)
from feedback import FeedbackSystem

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
REGISTRATION, TEACHER_PASSWORD, STUDENT_DATA, TEST_SUBMISSION = range(4)

class StepikBot:
    def __init__(self):
        self.db = Database()
        self.feedback_system = FeedbackSystem(self.db)
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        
        # ConversationHandler для регистрации
        registration_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_command)],
            states={
                REGISTRATION: [CallbackQueryHandler(self.registration_callback)],
                TEACHER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.teacher_password_handler)],
                STUDENT_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.student_data_handler)],
                TEST_SUBMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_command)]
        )
        
        # Обработчики команд
        self.application.add_handler(registration_handler)
        self.application.add_handler(CommandHandler('help', self.help_command))
        self.application.add_handler(CommandHandler('profile', self.profile_command))
        self.application.add_handler(CommandHandler('stats', self.stats_command))
        self.application.add_handler(CommandHandler('admin', self.admin_command))
        self.application.add_handler(CommandHandler('feedback', self.feedback_command))
        self.application.add_handler(CommandHandler('notifications', self.notifications_command))
        
        # Обработчики кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if user_data and user_data['is_approved']:
            # Пользователь уже зарегистрирован и одобрен
            await self.show_main_menu(update, context, user_data['role'])
            return ConversationHandler.END
        
        # Показываем меню регистрации
        keyboard = [
            [InlineKeyboardButton("👨‍🏫 Я преподаватель", callback_data="role_teacher")],
            [InlineKeyboardButton("👨‍🎓 Я студент", callback_data="role_student")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🎓 <b>Добро пожаловать в бот для оценки тестов Степика!</b>

Привет, {user.first_name}! 👋

Этот бот поможет:
• Студентам отправлять данные о пройденных тестах
• Преподавателям оценивать работы и выставлять баллы

Выберите свою роль:
        """
        
        await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
        return REGISTRATION
    
    async def registration_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора роли"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        role = query.data.split('_')[1]  # teacher или student
        
        context.user_data['role'] = role
        
        if role == 'teacher':
            await query.edit_message_text(
                "🔐 <b>Регистрация преподавателя</b>\n\n"
                "Введите пароль для регистрации преподавателя:",
                parse_mode='HTML'
            )
            return TEACHER_PASSWORD
        else:
            await query.edit_message_text(
                "👨‍🎓 <b>Регистрация студента</b>\n\n"
                "Введите ваше ФИО (например: Иванов Иван Иванович):",
                parse_mode='HTML'
            )
            return STUDENT_DATA
    
    async def teacher_password_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка пароля преподавателя"""
        password = update.message.text.strip()
        
        if password == ADMIN_PASSWORD:
            user = update.effective_user
            success = self.db.add_user(
                user.id, user.username or "", 
                user.first_name or "", user.last_name or "", 
                "teacher"
            )
            
            if success:
                self.db.approve_user(user.id)
                await update.message.reply_text(
                    "✅ <b>Регистрация успешна!</b>\n\n"
                    "Вы зарегистрированы как преподаватель. "
                    "Теперь вы можете просматривать и оценивать тесты студентов.",
                    parse_mode='HTML'
                )
                await self.show_teacher_menu(update, context)
                return ConversationHandler.END
            else:
                await update.message.reply_text("❌ Ошибка регистрации. Попробуйте еще раз.")
                return TEACHER_PASSWORD
        else:
            await update.message.reply_text(
                "❌ Неверный пароль. Попробуйте еще раз или введите /cancel для отмены."
            )
            return TEACHER_PASSWORD
    
    async def student_data_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка данных студента"""
        full_name = update.message.text.strip()
        
        if len(full_name.split()) < 2:
            await update.message.reply_text(
                "❌ Пожалуйста, введите полное ФИО (минимум имя и фамилию)."
            )
            return STUDENT_DATA
        
        user = update.effective_user
        success = self.db.add_user(
            user.id, user.username or "", 
            user.first_name or "", user.last_name or "", 
            "student"
        )
        
        if success:
            self.db.approve_user(user.id)
            context.user_data['full_name'] = full_name
            
            await update.message.reply_text(
                f"✅ <b>Регистрация успешна!</b>\n\n"
                f"Добро пожаловать, {full_name}!\n\n"
                "Теперь вы можете отправлять данные о пройденных тестах.\n\n"
                "Для отправки теста используйте команду /submit_test",
                parse_mode='HTML'
            )
            await self.show_student_menu(update, context)
            return ConversationHandler.END
        else:
            await update.message.reply_text("❌ Ошибка регистрации. Попробуйте еще раз.")
            return STUDENT_DATA
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, role: str):
        """Показ главного меню в зависимости от роли"""
        if role == 'teacher':
            await self.show_teacher_menu(update, context)
        else:
            await self.show_student_menu(update, context)
    
    async def show_teacher_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню преподавателя"""
        keyboard = [
            [InlineKeyboardButton("📋 Просмотр тестов", callback_data="view_tests")],
            [InlineKeyboardButton("👥 Выбрать студента", callback_data="select_student")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "👨‍🏫 <b>Панель преподавателя</b>\n\nВыберите действие:"
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def show_student_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню студента"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        # Получаем статистику студента
        student_tests = self.db.get_student_tests(user.id)
        total_tests = len(student_tests)
        reviewed_tests = len([t for t in student_tests if t['is_reviewed']])
        total_score = sum(t['score'] for t in student_tests if t['is_reviewed'])
        
        keyboard = [
            [InlineKeyboardButton("📤 Отправить тест", callback_data="submit_test")],
            [InlineKeyboardButton("📊 Мои результаты", callback_data="my_results")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "👨‍🎓 <b>Панель студента</b>\n\n"
        text += f"🎯 <b>Ваши баллы:</b> {total_score}\n"
        text += f"📝 <b>Отправлено тестов:</b> {total_tests}\n"
        text += f"✅ <b>Проверено:</b> {reviewed_tests}\n\n"
        text += "Выберите действие:"
        
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий кнопок"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if not user_data or not user_data['is_approved']:
            await query.edit_message_text("❌ Вы не зарегистрированы или не одобрены.")
            return
        
        action = query.data
        logger.info(f"Получен callback: {action}")
        
        if action == "view_tests" and user_data['role'] == 'teacher':
            await self.show_pending_tests(query, context)
        elif action == "select_student" and user_data['role'] == 'teacher':
            logger.info("Обрабатываем select_student для преподавателя")
            await self.show_student_selection(query, context)
        elif action == "submit_test" and user_data['role'] == 'student':
            await self.start_test_submission(query, context)
        elif action == "my_results" and user_data['role'] == 'student':
            await self.show_student_results(query, context)
        elif action == "help":
            await self.show_help(query, context)
        elif action.startswith("review_test_"):
            parts = action.split("_")
            logger.info(f"review_test_ action: {action}, parts: {parts}, len: {len(parts)}")
            if len(parts) >= 3:
                try:
                    test_id = int(parts[2])
                    await self.start_test_review(query, context, test_id)
                except (ValueError, IndexError) as e:
                    logger.error(f"Ошибка в review_test_: {e}")
                    await query.edit_message_text("❌ Ошибка в данных кнопки.")
            else:
                await query.edit_message_text("❌ Ошибка в данных кнопки.")
        elif action.startswith("score_"):
            parts = action.split("_")
            logger.info(f"score_ action: {action}, parts: {parts}, len: {len(parts)}")
            if len(parts) >= 4:
                try:
                    test_id = int(parts[2])
                    score = int(parts[3])
                    await self.set_test_score(query, context, test_id, score)
                except (ValueError, IndexError) as e:
                    logger.error(f"Ошибка в score_: {e}")
                    await query.edit_message_text("❌ Ошибка в данных кнопки.")
            else:
                await query.edit_message_text("❌ Ошибка в данных кнопки.")
        elif action == "feedback":
            await self.show_feedback_menu(query, context)
        elif action == "notifications":
            await self.show_notifications(query, context)
        elif action.startswith("feedback_"):
            parts = action.split("_")
            if len(parts) >= 2:
                feedback_type = parts[1]
                await self.start_feedback_submission(query, context, feedback_type)
            else:
                await query.edit_message_text("❌ Ошибка в данных кнопки.")
        elif action.startswith("rating_"):
            parts = action.split("_")
            if len(parts) >= 2:
                try:
                    rating = int(parts[1])
                    await self.submit_rating(query, context, rating)
                except ValueError:
                    await query.edit_message_text("❌ Ошибка в данных кнопки.")
            else:
                await query.edit_message_text("❌ Ошибка в данных кнопки.")
        elif action.startswith("student_"):
            parts = action.split("_")
            logger.info(f"Обрабатываем student_ callback: {action}, parts: {parts}")
            if len(parts) >= 2:
                try:
                    student_id = int(parts[1])
                    logger.info(f"Выбран студент с ID: {student_id}")
                    await self.show_student_details(query, context, student_id)
                except ValueError as e:
                    logger.error(f"Ошибка преобразования student_id: {e}")
                    await query.edit_message_text("❌ Ошибка в данных кнопки.")
            else:
                logger.error(f"Недостаточно частей в student_ callback: {parts}")
                await query.edit_message_text("❌ Ошибка в данных кнопки.")
        elif action == "back_to_main":
            await self.show_main_menu_from_callback(query, context)
        elif action == "back_to_teacher_menu":
            await self.show_teacher_menu_from_callback(query, context)
        elif action == "back_to_student_menu":
            await self.show_student_menu_from_callback(query, context)
    
    async def show_pending_tests(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ неоцененных тестов"""
        tests = self.db.get_pending_tests()
        
        if not tests:
            await query.edit_message_text("📋 Нет неоцененных тестов.")
            return
        
        text = "📋 <b>Неоцененные тесты:</b>\n\n"
        keyboard = []
        
        for test in tests[:10]:  # Показываем первые 10
            text += f"🆔 ID: {test['id']}\n"
            text += f"👤 Студент: {test['full_name']}\n"
            text += f"🆔 Степик ID: {test['stepik_id']}\n"
            text += f"🔗 Ссылка: {test['test_url']}\n"
            text += f"📝 Тип: {test['test_type']} баллов\n"
            text += f"📅 Дата: {test['submitted_at']}\n"
            text += "─" * 30 + "\n"
            
            keyboard.append([
                InlineKeyboardButton(f"Оценить тест #{test['id']}", callback_data=f"review_test_{test['id']}")
            ])
        
        # Добавляем кнопку "Назад"
        keyboard.append([InlineKeyboardButton("🔙 Назад к меню", callback_data="back_to_teacher_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def start_test_review(self, query, context: ContextTypes.DEFAULT_TYPE, test_id: int):
        """Начало оценки теста"""
        tests = self.db.get_pending_tests()
        test = next((t for t in tests if t['id'] == test_id), None)
        
        if not test:
            await query.edit_message_text("❌ Тест не найден.")
            return
        
        text = f"📝 <b>Оценка теста #{test_id}</b>\n\n"
        text += f"👤 Студент: {test['full_name']}\n"
        text += f"🆔 Степик ID: {test['stepik_id']}\n"
        text += f"🔗 Ссылка: {test['test_url']}\n"
        text += f"📝 Тип: {test['test_type']} баллов\n\n"
        text += "Выберите оценку:"
        
        # Получаем максимальный балл за тест
        max_score = int(test['test_type']) if test['test_type'] else 5
        
        keyboard = [
            [InlineKeyboardButton("❌ Не засчитать", callback_data=f"score_{test_id}_0")],
            [InlineKeyboardButton("✅ Засчитать", callback_data=f"score_{test_id}_{max_score}")],
            [InlineKeyboardButton("🔙 Назад к тестам", callback_data="view_tests")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def set_test_score(self, query, context: ContextTypes.DEFAULT_TYPE, test_id: int, score: int):
        """Установка оценки за тест"""
        try:
            logger.info(f"Начинаем оценку теста {test_id} с баллом {score}")
            
            # Сначала получаем информацию о тесте до его обновления
            tests = self.db.get_pending_tests()
            test = next((t for t in tests if t['id'] == test_id), None)
            
            if not test:
                logger.error(f"Тест {test_id} не найден в списке неоцененных")
                await query.edit_message_text("❌ Тест не найден.")
                return
            
            logger.info(f"Найден тест: {test}")
            
            success = self.db.review_test(test_id, score, "Оценено преподавателем")
            
            if success:
                logger.info(f"Тест {test_id} успешно оценен")
                
                # Упрощенное уведомление студенту
                try:
                    simple_message = f"Ваш тест #{test_id} оценен! Баллов: {score}"
                    self.feedback_system.send_notification(
                        test['student_id'],
                        simple_message,
                        'success'
                    )
                    logger.info(f"Уведомление отправлено студенту {test['student_id']}")
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления: {e}")
                
                keyboard = [[InlineKeyboardButton("🔙 Назад к тестам", callback_data="view_tests")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                if score > 0:
                    await query.edit_message_text(
                        f"✅ <b>Тест #{test_id} засчитан!</b>\n\n"
                        f"Баллов: {score}\n"
                        f"Студент получил уведомление.",
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                else:
                    await query.edit_message_text(
                        f"❌ <b>Тест #{test_id} не засчитан!</b>\n\n"
                        f"Баллов: 0\n"
                        f"Студент получил уведомление.",
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
            else:
                logger.error(f"Ошибка при оценке теста {test_id}")
                await query.edit_message_text("❌ Ошибка при оценке теста.")
                
        except Exception as e:
            logger.error(f"Критическая ошибка в set_test_score: {e}")
            await query.edit_message_text("❌ Произошла ошибка при оценке теста.")
    
    async def show_teacher_statistics(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ статистики для преподавателя"""
        stats = self.db.get_statistics()
        feedback_stats = self.feedback_system.get_feedback_stats()
        
        text = format_statistics_summary(stats)
        
        if feedback_stats:
            text += "\n💬 <b>Обратная связь:</b>\n"
            text += f"📝 Всего отзывов: {feedback_stats.get('total_feedback', 0)}\n"
            text += f"⭐ Средняя оценка: {feedback_stats.get('average_rating', 0)}\n"
            text += f"⏳ Необработано: {feedback_stats.get('unprocessed_feedback', 0)}"
        
        await query.edit_message_text(text, parse_mode='HTML')
    
    async def show_students_scores(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ баллов всех студентов"""
        students = self.db.get_students_scores()
        
        if not students:
            await query.edit_message_text("👥 Нет зарегистрированных студентов.")
            return
        
        text = "🏆 <b>Баллы студентов:</b>\n\n"
        
        for i, student in enumerate(students, 1):
            # Формируем имя студента
            first_name = student['first_name'] or ''
            last_name = student['last_name'] or ''
            name = f"{first_name} {last_name}".strip()
            
            if not name:
                name = f"Студент #{student['user_id']}"
            
            text += f"{i}. <b>{name}</b>\n"
            text += f"   🆔 Степик ID: {student.get('stepik_id', 'Не указан')}\n"
            text += f"   🎯 Баллов: {student['total_score']}\n"
            text += f"   📝 Тестов: {student['reviewed_tests']}/{student['total_tests']}\n"
            
            if student['total_tests'] > 0:
                percentage = (student['reviewed_tests'] / student['total_tests']) * 100
                text += f"   📊 Выполнено: {percentage:.1f}%\n"
            
            text += "─" * 30 + "\n"
        
        # Добавляем общую статистику
        total_score = sum(s['total_score'] for s in students)
        text += f"\n📈 <b>Общая статистика:</b>\n"
        text += f"👥 Студентов: {len(students)}\n"
        text += f"🎯 Всего баллов: {total_score}\n"
        text += f"📊 Средний балл: {total_score / len(students) if students else 0:.1f}"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад к меню", callback_data="back_to_teacher_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def show_student_selection(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ списка студентов для выбора"""
        try:
            logger.info("Начинаем показ списка студентов")
            students = self.db.get_students_scores()
            logger.info(f"Получено студентов: {len(students) if students else 0}")
            
            if not students:
                logger.info("Список студентов пуст")
                await query.edit_message_text("👥 Нет зарегистрированных студентов.")
                return
            
            text = "👥 <b>Выберите студента для просмотра:</b>\n\n"
            
            keyboard = []
            for student in students:
                # Формируем имя студента
                first_name = student['first_name'] or ''
                last_name = student['last_name'] or ''
                name = f"{first_name} {last_name}".strip()
                
                if not name:
                    name = f"Студент #{student['user_id']}"
                
                button_text = f"{name} ({student['total_score']} баллов)"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"student_{student['user_id']}")])
                logger.info(f"Добавлен студент: {name} (ID: {student['user_id']})")
            
            keyboard.append([InlineKeyboardButton("🔙 Назад к меню", callback_data="back_to_teacher_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
            logger.info("Список студентов успешно отображен")
            
        except Exception as e:
            logger.error(f"Ошибка в show_student_selection: {e}")
            await query.edit_message_text("❌ Ошибка при загрузке списка студентов.")
    
    async def show_student_details(self, query, context: ContextTypes.DEFAULT_TYPE, student_id: int):
        """Показ детальной информации о студенте"""
        # Получаем информацию о студенте
        student_data = self.db.get_user(student_id)
        if not student_data:
            await query.edit_message_text("❌ Студент не найден.")
            return
        
        # Получаем все тесты студента
        student_tests = self.db.get_student_tests(student_id)
        
        # Формируем имя студента
        first_name = student_data['first_name'] or ''
        last_name = student_data['last_name'] or ''
        name = f"{first_name} {last_name}".strip()
        
        if not name:
            name = f"Студент #{student_id}"
        
        text = f"👤 <b>Информация о студенте:</b>\n\n"
        text += f"📝 <b>Имя:</b> {name}\n"
        text += f"🆔 <b>Степик ID:</b> {student_data['stepik_id'] or 'Не указан'}\n"
        text += f"📧 <b>Telegram ID:</b> {student_id}\n\n"
        
        # Подсчитываем статистику
        total_tests = len(student_tests)
        reviewed_tests = len([t for t in student_tests if t['is_reviewed']])
        total_score = sum(t['score'] for t in student_tests if t['is_reviewed'])
        
        text += f"📊 <b>Статистика:</b>\n"
        text += f"🎯 <b>Всего баллов:</b> {total_score}\n"
        text += f"📝 <b>Всего тестов:</b> {total_tests}\n"
        text += f"✅ <b>Проверено:</b> {reviewed_tests}\n"
        text += f"⏳ <b>На проверке:</b> {total_tests - reviewed_tests}\n\n"
        
        if total_tests > 0:
            percentage = (reviewed_tests / total_tests) * 100
            text += f"📈 <b>Выполнено:</b> {percentage:.1f}%\n\n"
        
        # Показываем последние тесты
        if student_tests:
            text += f"📋 <b>Последние тесты:</b>\n"
            for i, test in enumerate(student_tests[:5], 1):  # Показываем только последние 5
                status = "✅" if test['is_reviewed'] else "⏳"
                score_text = f"{test['score']} баллов" if test['is_reviewed'] else "На проверке"
                text += f"{i}. {status} Тест #{test['id']} - {score_text}\n"
            
            if total_tests > 5:
                text += f"... и еще {total_tests - 5} тестов\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад к выбору", callback_data="select_student")],
            [InlineKeyboardButton("🔙 Назад к меню", callback_data="back_to_teacher_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def start_test_submission(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Начало отправки теста"""
        text = format_test_submission_guide()
        keyboard = [[InlineKeyboardButton("🔙 Назад к меню", callback_data="back_to_student_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def show_student_results(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ результатов студента"""
        user = query.from_user
        tests = self.db.get_student_tests(user.id)
        
        if not tests:
            await query.edit_message_text("📊 У вас пока нет отправленных тестов.")
            return
        
        text = "📊 <b>Ваши результаты:</b>\n\n"
        total_score = 0
        reviewed_count = 0
        
        for test in tests:
            text += f"🆔 Тест #{test['id']}\n"
            text += f"🔗 {test['test_url']}\n"
            text += f"📝 Тип: {test['test_type']} баллов\n"
            
            if test['is_reviewed']:
                text += f"✅ Оценка: {test['score']} баллов\n"
                if test['teacher_comment']:
                    text += f"💬 Комментарий: {test['teacher_comment']}\n"
                total_score += test['score']
                reviewed_count += 1
            else:
                text += "⏳ Ожидает оценки\n"
            
            text += "─" * 30 + "\n"
        
        if reviewed_count > 0:
            text += f"\n📈 <b>Итого:</b> {total_score} баллов из {reviewed_count} тестов"
        else:
            text += f"\n📈 <b>Итого:</b> 0 баллов (тесты не оценены)"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад к меню", callback_data="back_to_student_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def show_help(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ справки"""
        text = """
ℹ️ <b>Справка по боту</b>

<b>Для студентов:</b>
• /submit_test - отправить тест
• /my_results - посмотреть результаты
• /profile - информация о профиле

<b>Для преподавателей:</b>
• Просмотр неоцененных тестов
• Оценка тестов (0-5 баллов)
• Статистика по студентам

<b>Формат отправки теста:</b>
<code>ФИО: Иванов Иван Иванович
ID Степика: 123456
Ссылка на тест: https://stepik.org/lesson/123456/step/1
Тип теста: 3</code>
        """
        keyboard = [[InlineKeyboardButton("🔙 Назад к меню", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if not user_data or not user_data['is_approved']:
            await update.message.reply_text("❌ Вы не зарегистрированы. Используйте /start для регистрации.")
            return
        
        text = update.message.text.strip()
        
        # Проверяем, является ли сообщение отправкой теста
        if self.is_test_submission(text):
            await self.process_test_submission(update, context, text)
        # Проверяем, является ли сообщение обратной связью
        elif 'feedback_type' in context.user_data:
            await self.process_feedback_submission(update, context, text)
        else:
            await update.message.reply_text(
                "❓ Не понимаю команду. Используйте /help для получения справки."
            )
    
    def is_test_submission(self, text: str) -> bool:
        """Проверка, является ли текст отправкой теста"""
        lines = text.split('\n')
        required_fields = ['ФИО:', 'ID Степика:', 'Ссылка на тест:', 'Тип теста:']
        return all(any(field in line for line in lines) for field in required_fields)
    
    async def process_test_submission(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка отправки теста"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if user_data['role'] != 'student':
            await update.message.reply_text("❌ Только студенты могут отправлять тесты.")
            return
        
        try:
            # Парсим данные
            lines = text.split('\n')
            data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
            
            # Валидируем данные
            validation = validate_test_data(data)
            if not validation['is_valid']:
                await update.message.reply_text(
                    f"❌ Ошибки в данных:\n" + "\n".join(validation['errors'])
                )
                return
            
            test_type = data['Тип теста']
            test_url = data['Ссылка на тест']
            
            # Сохраняем тест
            success = self.db.add_test(
                user.id,
                data['ФИО'],
                data['ID Степика'],
                test_url,
                test_type
            )
            
            if success:
                # Получаем обновленную статистику студента
                student_tests = self.db.get_student_tests(user.id)
                total_tests = len(student_tests)
                reviewed_tests = len([t for t in student_tests if t['is_reviewed']])
                total_score = sum(t['score'] for t in student_tests if t['is_reviewed'])
                
                keyboard = [
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_student_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "✅ <b>Тест успешно отправлен!</b>\n\n"
                    f"👤 ФИО: {data['ФИО']}\n"
                    f"🆔 ID Степика: {data['ID Степика']}\n"
                    f"🔗 Ссылка: {test_url}\n"
                    f"📝 Тип: {test_type} баллов\n\n"
                    f"📊 <b>Ваша статистика:</b>\n"
                    f"🎯 Баллов: {total_score}\n"
                    f"📝 Тестов отправлено: {total_tests}\n"
                    f"✅ Проверено: {reviewed_tests}\n\n"
                    "Преподаватель оценит ваш тест в ближайшее время.",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("❌ Ошибка при сохранении теста.")
                
        except Exception as e:
            logger.error(f"Ошибка обработки теста: {e}")
            await update.message.reply_text("❌ Ошибка при обработке данных теста.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        await self.show_help(update, context)
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /profile"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text("❌ Вы не зарегистрированы.")
            return
        
        role_emoji = "👨‍🏫" if user_data['role'] == 'teacher' else "👨‍🎓"
        role_text = "Преподаватель" if user_data['role'] == 'teacher' else "Студент"
        
        text = f"""
👤 <b>Ваш профиль</b>

{role_emoji} Роль: {role_text}
🆔 ID: {user.id}
👤 Имя: {user.first_name} {user.last_name or ''}
📅 Регистрация: {user_data['created_at']}
✅ Статус: {'Одобрен' if user_data['is_approved'] else 'Ожидает одобрения'}
        """
        
        await update.message.reply_text(text, parse_mode='HTML')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if not user_data or user_data['role'] != 'teacher':
            await update.message.reply_text("❌ Доступно только преподавателям.")
            return
        
        await self.show_teacher_statistics(update, context)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /admin"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if not user_data or user_data['role'] != 'teacher':
            await update.message.reply_text("❌ Доступно только преподавателям.")
            return
        
        stats = self.db.get_statistics()
        text = f"""
🔧 <b>Админ панель</b>

📊 Статистика:
• Студентов: {stats.get('total_students', 0)}
• Тестов: {stats.get('total_tests', 0)}
• Оценено: {stats.get('reviewed_tests', 0)}
• Ожидает: {stats.get('pending_tests', 0)}

🛠️ Доступные команды:
• /stats - статистика
• /profile - профиль
        """
        
        await update.message.reply_text(text, parse_mode='HTML')
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /cancel"""
        await update.message.reply_text("❌ Операция отменена.")
        return ConversationHandler.END
    
    async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /feedback"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if not user_data or not user_data['is_approved']:
            await update.message.reply_text("❌ Вы не зарегистрированы.")
            return
        
        keyboard = self.feedback_system.get_feedback_form_keyboard()
        text = "💬 <b>Обратная связь</b>\n\nВыберите тип сообщения:"
        
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=keyboard)
    
    async def notifications_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /notifications"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if not user_data or not user_data['is_approved']:
            await update.message.reply_text("❌ Вы не зарегистрированы.")
            return
        
        notifications = self.feedback_system.get_user_notifications(user.id)
        
        if not notifications:
            await update.message.reply_text("🔔 У вас нет новых уведомлений.")
            return
        
        text = "🔔 <b>Ваши уведомления:</b>\n\n"
        
        for notif in notifications:
            emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'success': '✅',
                'error': '❌'
            }.get(notif['notification_type'], '📢')
            
            text += f"{emoji} {notif['message']}\n"
            text += f"📅 {notif['created_at']}\n\n"
        
        await update.message.reply_text(text, parse_mode='HTML')
    
    async def show_feedback_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню обратной связи"""
        keyboard = self.feedback_system.get_feedback_form_keyboard()
        text = "💬 <b>Обратная связь</b>\n\nВыберите тип сообщения:"
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
    
    async def show_notifications(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ уведомлений"""
        user = query.from_user
        notifications = self.feedback_system.get_user_notifications(user.id)
        
        if not notifications:
            await query.edit_message_text("🔔 У вас нет новых уведомлений.")
            return
        
        text = "🔔 <b>Ваши уведомления:</b>\n\n"
        
        for notif in notifications:
            emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'success': '✅',
                'error': '❌'
            }.get(notif['notification_type'], '📢')
            
            text += f"{emoji} {notif['message']}\n"
            text += f"📅 {notif['created_at']}\n\n"
        
        await query.edit_message_text(text, parse_mode='HTML')
    
    async def start_feedback_submission(self, query, context: ContextTypes.DEFAULT_TYPE, feedback_type: str):
        """Начало отправки отзыва"""
        context.user_data['feedback_type'] = feedback_type
        
        type_names = {
            'bug': '🐛 Сообщение об ошибке',
            'suggestion': '💡 Предложение',
            'compliment': '👍 Похвала',
            'question': '❓ Вопрос'
        }
        
        text = f"{type_names.get(feedback_type, '💬 Отзыв')}\n\n"
        text += "Напишите ваше сообщение:"
        
        await query.edit_message_text(text, parse_mode='HTML')
    
    async def submit_rating(self, query, context: ContextTypes.DEFAULT_TYPE, rating: int):
        """Отправка оценки бота"""
        user = query.from_user
        success = self.feedback_system.submit_feedback(
            user.id, 'rating', f"Оценка бота: {rating} звезд", rating
        )
        
        if success:
            await query.edit_message_text(
                f"⭐ <b>Спасибо за оценку!</b>\n\n"
                f"Вы оценили бота на {rating} звезд. "
                "Ваше мнение поможет улучшить работу бота!",
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text("❌ Ошибка при отправке оценки.")
    
    async def process_feedback_submission(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка отправки обратной связи"""
        user = update.effective_user
        feedback_type = context.user_data.get('feedback_type')
        
        if not feedback_type:
            await update.message.reply_text("❌ Ошибка: тип обратной связи не определен.")
            return
        
        success = self.feedback_system.submit_feedback(user.id, feedback_type, text)
        
        if success:
            # Очищаем данные
            context.user_data.pop('feedback_type', None)
            
            await update.message.reply_text(
                "✅ <b>Спасибо за обратную связь!</b>\n\n"
                "Ваше сообщение получено и будет рассмотрено. "
                "Мы ценим ваше мнение!",
                parse_mode='HTML'
            )
            
            # Отправляем уведомление преподавателям
            await self.notify_teachers_about_feedback(feedback_type, text)
        else:
            await update.message.reply_text("❌ Ошибка при отправке сообщения.")
    
    async def notify_teachers_about_feedback(self, feedback_type: str, message: str):
        """Уведомление преподавателей о новой обратной связи"""
        try:
            # Получаем всех преподавателей
            import sqlite3
            with sqlite3.connect(self.db.db_name) as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT user_id FROM users WHERE role = "teacher" AND is_approved = TRUE')
                teachers = cursor.fetchall()
            
            # Отправляем уведомления
            for teacher_id, in teachers:
                self.feedback_system.send_notification(
                    teacher_id,
                    f"Новая обратная связь ({feedback_type}): {message[:100]}...",
                    'info'
                )
        except Exception as e:
            logger.error(f"Ошибка уведомления преподавателей: {e}")
    
    async def show_main_menu_from_callback(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Показ главного меню из callback"""
        user = query.from_user
        user_data = self.db.get_user(user.id)
        
        if user_data and user_data['is_approved']:
            if user_data['role'] == 'teacher':
                await self.show_teacher_menu_from_callback(query, context)
            else:
                await self.show_student_menu_from_callback(query, context)
        else:
            await query.edit_message_text("❌ Вы не зарегистрированы. Используйте /start для регистрации.")
    
    async def show_teacher_menu_from_callback(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Меню преподавателя из callback"""
        keyboard = [
            [InlineKeyboardButton("📋 Просмотр тестов", callback_data="view_tests")],
            [InlineKeyboardButton("👥 Выбрать студента", callback_data="select_student")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "👨‍🏫 <b>Панель преподавателя</b>\n\nВыберите действие:"
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def show_student_menu_from_callback(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Меню студента из callback"""
        user = query.from_user
        user_data = self.db.get_user(user.id)
        
        # Получаем статистику студента
        student_tests = self.db.get_student_tests(user.id)
        total_tests = len(student_tests)
        reviewed_tests = len([t for t in student_tests if t['is_reviewed']])
        total_score = sum(t['score'] for t in student_tests if t['is_reviewed'])
        
        keyboard = [
            [InlineKeyboardButton("📤 Отправить тест", callback_data="submit_test")],
            [InlineKeyboardButton("📊 Мои результаты", callback_data="my_results")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "👨‍🎓 <b>Панель студента</b>\n\n"
        text += f"🎯 <b>Ваши баллы:</b> {total_score}\n"
        text += f"📝 <b>Отправлено тестов:</b> {total_tests}\n"
        text += f"✅ <b>Проверено:</b> {reviewed_tests}\n\n"
        text += "Выберите действие:"
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Ошибка при обработке обновления: {context.error}")
        
        # Пытаемся отправить сообщение об ошибке пользователю
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Произошла ошибка. Попробуйте еще раз или используйте /start для перезапуска."
                )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск бота...")
        try:
            # Используем asyncio для запуска
            import asyncio
            asyncio.run(self._run_async())
        except Exception as e:
            logger.error(f"Ошибка запуска: {e}")
            # Fallback к простому запуску
            try:
                self.application.run_polling()
            except Exception as e2:
                logger.error(f"Fallback запуск не удался: {e2}")
    
    async def _run_async(self):
        """Асинхронный запуск бота"""
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Бот запущен и работает!")
            
            # Ждем бесконечно, пока бот работает
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки...")
                await self.application.stop()
                await self.application.shutdown()
                
        except Exception as e:
            logger.error(f"Ошибка асинхронного запуска: {e}")
            raise

if __name__ == '__main__':
    bot = StepikBot()
    bot.run()
