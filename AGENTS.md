# AGENTS.md

## Описание проекта
Проект состоит из Nuxt 4 фронтенда и Django бэкенда для бронирования мест на события. Фронтенд общается с Django через серверные роуты Nuxt (`/api/backend/...`), которые проксируют запросы к `/api/...` на бэкенде. Аутентификация JWT реализована на стороне клиента с обновлением access токена через refresh.

На стороне `accounts` дополнительно есть отдельные модели `UserGroup` и `UserProfile`. Группы пользователей не связаны с Django auth groups, редактируются через Django admin и используются на форме регистрации Nuxt.

## Структура репозитория
- `frontend/`: Nuxt приложение (UI, страницы, stores, server routes).
- `backend/`: Django приложение (accounts, booking, настройки).
- `scripts/`: вспомогательные скрипты.
- `docker-compose.yml`: инфраструктура для запуска с Postgres и Traefik.

## Ключевые маршруты API
- `POST /api/accounts/token/`: получить access/refresh.
- `POST /api/accounts/token/refresh/`: обновить access.
- `GET /api/accounts/signup-groups/`: получить список групп для регистрации.
- `POST /api/accounts/signup/`: регистрация.
- `GET /api/accounts/me/`: профиль.
- `GET /api/booking/events/`: список событий.
- `GET /api/booking/events/<id>/seatmap/`: карта мест.
- `POST /api/booking/hold/`: удержание места.
- `POST /api/booking/bookings/<id>/release/`: удалить удержанную или подтвержденную бронь пользователя.

## Команды разработки
Frontend:
- `cd frontend`
- `npm install`
- `npm run dev`

Backend:
- `cd backend`
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py runserver`

## Docker запуск
- Скопировать `.env.example` в `.env` и заполнить значения.
- Запустить `docker compose up -d --build`.

## Переменные окружения
Docker-compose использует:
- `TRAEFIK_ACME_EMAIL`, `TRAEFIK_WEB_HOST`, `TRAEFIK_API_HOST`.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`.
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_CORS_ALLOWED_ORIGINS`.

Frontend runtime config:
- `NUXT_BACKEND_URL` (или `BACKEND_URL` в контейнере) — URL Django.

## Примечания по аутентификации
JWT хранится в Pinia store. Перед запросами к защищенным эндпоинтам используется обновление access токена, затем добавляется `Authorization: Bearer <token>`.

## Примечания по регистрации
- Регистрация на фронтенде требует `username`, `password`, `group`, `full_name`, `child_full_name`.
- Список групп для регистрации загружается публично через `/api/accounts/signup-groups/`.
- Данные группы, ФИО пользователя и ФИО ребенка сохраняются в `accounts.UserProfile`.

## Примечания по бронированиям
- У бронирований нет статуса `canceled/cancelled`.
- При отмене или освобождении бронь удаляется из БД через release endpoint.
