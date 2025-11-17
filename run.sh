#!/bin/bash

# --- JobTracker-Bot Run Script ---

# 0. Ожидание готовности БД
# Ждем 5 секунд, пока Postgres гарантированно поднимется.
echo "Waiting for DB to be ready..."
sleep 5
echo "Waiting complete. Starting migrations..."

# 1. Запуск миграций Alembic
echo "Applying database migrations using Alembic..."
# Команда Alembic должна работать, т.к. Poetry и Alembic установлены.
poetry run alembic upgrade head
MIGRATION_STATUS=$?

if [ $MIGRATION_STATUS -ne 0 ]; then
    echo "Alembic migrations failed! Exiting."
    # Если миграции не прошли, контейнер завершит работу.
    exit 1
fi
echo "Alembic migrations applied successfully. ✅"

# 2. Запуск FastAPI API
echo "Starting FastAPI API..."
# Запускаем API в фоновом режиме
poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "FastAPI API started with PID: $API_PID"

# 3. Запуск Telegram Bot
echo "Starting Telegram Bot..."
# Запускаем бота в фоновом режиме, указывая путь к файлу
poetry run python -m app.bot.bot &
BOT_PID=$!
echo "Telegram Bot started with PID: $BOT_PID"

# Функция-обработчик для корректного завершения
cleanup() {
    echo "Stopping processes..."
    # Отправляем сигнал завершения обоим процессам
    kill -SIGTERM $API_PID $BOT_PID 2>/dev/null
    wait $API_PID $BOT_PID 2>/dev/null
    echo "Processes stopped."
    exit 0
}

# Отслеживаем сигналы завершения (SIGINT, SIGTERM)
trap cleanup SIGINT SIGTERM

# Ожидание (PID 1)
# Ждем, пока один из фоновых процессов не завершится
wait -n $API_PID $BOT_PID
cleanup