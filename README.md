# KitsunePlay — Backend

Flask + SQLAlchemy + JWT REST API для аниме-сайта.

---

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Создать .env файл
cp .env.example .env
# (при желании отредактировать .env)

# 3. Заполнить базу данных
python seed.py

# 4. Запустить сервер
python app.py
```

Сервер запустится на `http://localhost:5000`

---

## Структура проекта

```
kitsune_backend/
├── app.py              — точка входа, создание Flask app
├── config.py           — настройки (БД, JWT, CORS)
├── models.py           — модели базы данных
├── seed.py             — заполнение БД из Jikan API
├── requirements.txt
├── .env.example        — пример переменных окружения
└── routes/
    ├── auth.py         — авторизация
    ├── anime.py        — каталог аниме
    ├── collections.py  — списки пользователя
    └── ratings.py      — оценки
```

---

## API Reference

### Авторизация

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |
| GET  | `/api/auth/me` | Текущий пользователь 🔒 |
| PATCH| `/api/auth/me` | Обновить профиль 🔒 |
| POST | `/api/auth/change-password` | Сменить пароль 🔒 |

**Регистрация:**
```json
POST /api/auth/register
{ "username": "user", "email": "user@mail.ru", "password": "123456" }

Ответ: { "token": "...", "user": { "id": 1, "username": "user", ... } }
```

**Вход:**
```json
POST /api/auth/login
{ "username": "admin", "password": "admin123" }
```

> 🔒 Защищённые маршруты требуют заголовок:
> `Authorization: Bearer <token>`

---

### Аниме

| Метод  | URL | Описание |
|--------|-----|----------|
| GET    | `/api/anime` | Список с фильтрами и пагинацией |
| GET    | `/api/anime/<id>` | Детальная страница |
| POST   | `/api/anime` | Добавить аниме 🔒👑 |
| PUT    | `/api/anime/<id>` | Обновить аниме 🔒👑 |
| DELETE | `/api/anime/<id>` | Удалить аниме 🔒👑 |
| GET    | `/api/anime/schedule` | Расписание |
| GET    | `/api/anime/genres` | Список жанров |

**Параметры GET /api/anime:**
```
?q=наруто          — поиск по названию
&genre=Action      — фильтр по жанру
&status=ongoing    — ongoing / finished / announced
&year=2023         — год выхода
&studio=MAPPA      — студия
&min_rating=8      — минимальный рейтинг
&sort=rating       — rating / popular / year / name
&page=1
&per_page=24
```

---

### Коллекции 🔒

| Метод  | URL | Описание |
|--------|-----|----------|
| GET    | `/api/collections` | Моя коллекция |
| GET    | `/api/collections/stats` | Счётчики по статусам |
| POST   | `/api/collections` | Добавить / обновить запись |
| DELETE | `/api/collections/<anime_id>` | Удалить из коллекции |
| PATCH  | `/api/collections/<anime_id>/progress` | Обновить прогресс |

**Статусы:** `watching` · `planned` · `watched` · `dropped` · `hold` · `fav`

```json
POST /api/collections
{ "anime_id": 1, "status": "watching", "episodes_watched": 5 }
```

---

### Оценки 🔒

| Метод  | URL | Описание |
|--------|-----|----------|
| GET    | `/api/ratings` | Мои оценки |
| GET    | `/api/ratings/<anime_id>` | Моя оценка для аниме |
| POST   | `/api/ratings` | Поставить оценку (1–10) |
| DELETE | `/api/ratings/<anime_id>` | Удалить оценку |
| GET    | `/api/ratings/anime/<id>/stats` | Статистика оценок |

```json
POST /api/ratings
{ "anime_id": 1, "score": 9 }
```

---

## База данных

**Таблицы:**
- `user` — пользователи
- `anime` — каталог аниме
- `genre` — жанры
- `anime_genres` — связь аниме ↔ жанры (many-to-many)
- `stream_link` — ссылки на стриминги
- `schedule_entry` — расписание выхода серий
- `collection` — списки пользователей
- `rating` — оценки

**Переключение на PostgreSQL:**
```
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/kitsune
```

---

## Демо-аккаунт

```
Логин:  admin
Пароль: admin123
Роль:   admin (доступ к POST/PUT/DELETE аниме)
```
