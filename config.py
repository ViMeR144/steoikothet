import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Database
DATABASE_NAME = 'stepik_bot.db'

# Admin settings
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Bot settings
MAX_STUDENTS = 100
MAX_TESTS_PER_STUDENT = 50


