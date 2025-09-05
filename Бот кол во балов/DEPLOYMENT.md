# Инструкция по развертыванию

## Локальное развертывание

### 1. Подготовка окружения

```bash
# Клонирование репозитория
git clone <repository-url>
cd stepik-telegram-bot

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Копирование файла примера
cp .env.example .env

# Редактирование .env файла
nano .env
```

Заполните файл `.env`:
```
BOT_TOKEN=your_bot_token_here
ADMIN_PASSWORD=your_secure_password
```

### 3. Получение токена бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

### 4. Запуск бота

```bash
# Тестирование
python test_bot.py

# Запуск бота
python run.py
```

## Развертывание на хостинге

### Heroku

1. Установите Heroku CLI
2. Создайте приложение:
```bash
heroku create your-bot-name
```

3. Установите переменные окружения:
```bash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set ADMIN_PASSWORD=your_password
```

4. Разверните приложение:
```bash
git push heroku main
```

### Docker

```bash
# Сборка образа
docker build -t stepik-bot .

# Запуск контейнера
docker run -d \
  --name stepik-bot \
  -e BOT_TOKEN=your_bot_token \
  -e ADMIN_PASSWORD=your_password \
  -v $(pwd)/data:/app/data \
  stepik-bot
```

### Docker Compose

```bash
# Запуск с docker-compose
docker-compose up -d
```

### VPS/Сервер

1. Загрузите файлы на сервер
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте systemd сервис:
```bash
sudo cp stepik-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stepik-bot
sudo systemctl start stepik-bot
```

## Мониторинг и логи

### Просмотр логов

```bash
# Docker
docker logs stepik-bot

# Systemd
sudo journalctl -u stepik-bot -f

# Heroku
heroku logs --tail
```

### Мониторинг состояния

```bash
# Проверка статуса
sudo systemctl status stepik-bot

# Перезапуск
sudo systemctl restart stepik-bot
```

## Безопасность

### Рекомендации

1. Используйте сложный пароль для преподавателей
2. Регулярно обновляйте зависимости
3. Настройте бэкапы базы данных
4. Используйте HTTPS для веб-интерфейса (если есть)

### Бэкапы

```bash
# Создание бэкапа базы данных
cp stepik_bot.db backup_$(date +%Y%m%d_%H%M%S).db

# Автоматический бэкап (cron)
0 2 * * * cp /path/to/stepik_bot.db /path/to/backups/backup_$(date +\%Y\%m\%d).db
```

## Обновление

1. Остановите бота
2. Создайте бэкап базы данных
3. Обновите код
4. Установите новые зависимости
5. Запустите бота

```bash
# Остановка
sudo systemctl stop stepik-bot

# Бэкап
cp stepik_bot.db backup_$(date +%Y%m%d).db

# Обновление
git pull
pip install -r requirements.txt

# Запуск
sudo systemctl start stepik-bot
```

## Устранение неполадок

### Частые проблемы

1. **Бот не отвечает**
   - Проверьте токен бота
   - Убедитесь, что бот запущен
   - Проверьте логи

2. **Ошибки базы данных**
   - Проверьте права доступа к файлу БД
   - Убедитесь, что директория существует

3. **Проблемы с зависимостями**
   - Обновите pip: `pip install --upgrade pip`
   - Переустановите зависимости: `pip install -r requirements.txt --force-reinstall`

### Логи и отладка

```bash
# Включение подробных логов
export PYTHONPATH=/path/to/bot
python -u run.py

# Отладка базы данных
sqlite3 stepik_bot.db
.tables
.schema users
```


