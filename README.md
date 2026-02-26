# Email AI Support System

Короткое описание
------------------

AI-пайплайн для обработки входящей корпоративной почты: система принимает письма, сохраняет их в базе, анализирует через ML-модуль и отображает результаты в веб-интерфейсе для операторов поддержки.

Содержание
---------
- [Быстрый старт](#быстрый-старт)
- [Функционал](#функционал)
- [Архитектура](#архитектура)
- [Переменные окружения](#переменные-окружения)
- [Запуск локально (Docker)](#запуск-локально-docker)
- [Риски и замечания](#риски-и-замечания)

## Функционал

- Автоматическая обработка писем и классификация (ML)
- Автоответы при низкой сложности и создание тикетов для сложных запросов
- Хранение истории и статусов в PostgreSQL
- Read-only панель оператора с фильтрами и экспортом (CSV/XLSX)

## Архитектура

```
Email -> Backend (IMAP polling) -> ML Service -> Backend -> PostgreSQL -> Frontend
```

Компоненты:
- `backend`: FastAPI (IMAP polling, API, ML mock)
- `ml-service`: модуль анализа писем (можно заменить реальным LLM)
- `postgres`: база данных
- `frontend`: React + Vite  read-only dashboard

## Быстрый старт

1. Скопируйте пример окружения:

```bash
cp .env.example .env
```

2. Отредактируйте `.env` и задайте реальные значения IMAP/DB при необходимости.

3. Запустите через Docker Compose:

```bash
docker-compose up --build
```

4. Откройте:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Переменные окружения

Пример (см. `.env.example`):

```
POSTGRES_DB=email_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_EMAIL=your-email@gmail.com
IMAP_PASSWORD=your-app-password
IMAP_FOLDER=INBOX
IMAP_POLL_INTERVAL=30

ML_SERVICE_URL=http://backend:8000/api/v1/ml/analyze
```

## Замена ML-модуля

ML-модуль реализован в `backend/app/services/ml_service.py`. Для интеграции реальной модели замените реализацию функции `analyze_email()` или заведите отдельный сервис и укажите его URL в `ML_SERVICE_URL`.

## Риски и рекомендации

- Ограниченная база знаний может приводить к некорректным ответам  добавляйте кейсы по мере работы и держите контроль качества.
- На хакатоне ограничено время  сначала делаем минимально рабочую интеграцию Backend + Frontend; ML можно подключать позже.

## Контакты

Если нужно изменить README дальше  скажите, что добавить: бейджи, GIF-демо, скриншоты или CI-инструкции.
