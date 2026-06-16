# KitsunePlay — Backend — Деплой на Render

## Шаги

### 1. Загрузи на GitHub
- Создай аккаунт на github.com
- New repository → назови `kitsune-backend`
- Загрузи все файлы из этой папки

### 2. Задеплой на Render
- render.com → New → Web Service
- Подключи GitHub репозиторий `kitsune-backend`
- Настройки:
  - **Runtime:** Python
  - **Build Command:** `./build.sh`
  - **Start Command:** `gunicorn app:app`
  - **Plan:** Free

### 3. База данных
- Render → New → PostgreSQL (Free)
- Название: `kitsune-db`
- Скопируй **Internal Database URL**
- В настройках Web Service → Environment → добавь:
  - `DATABASE_URL` = (Internal Database URL)
  - `JWT_SECRET_KEY` = (любая случайная строка)
  - `SECRET_KEY` = (любая случайная строка)
  - `CORS_ORIGINS` = `*`

### 4. После деплоя
- Скопируй URL бэкенда (например `https://kitsune-backend.onrender.com`)
- Вставь его в `app.js` фронтенда вместо `https://kitsune-backend.onrender.com`
- Задеплой фронтенд как Static Site

## Логин администратора
- Логин: `admin`
- Пароль: `admin123`
