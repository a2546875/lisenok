# Лисёнок — Дыхание леса

Публичный репозиторий: [github.com/a2546875/lisenok](https://github.com/a2546875/lisenok)

Сайт авторского гипсового декора: витрина, конструктор набора и админка.

Стек: **FastAPI**, **SQLAlchemy**, **Streamlit**, **PostgreSQL** (на сервере) / **SQLite** (локально).

## Возможности

- Витрина с розницей и оптом
- Конструктор набора: состав, цвет гипса, узор
- Корзина и заявка с сайта
- Админка: каталог, опции конструктора, заявки
- Готово к переносу на VDS: переменные окружения и `docker-compose` для PostgreSQL

## Быстрый старт на Windows

```powershell
cd "$env:USERPROFILE\Desktop\лисенок"
.\start-site.ps1
```

Сайт: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Админка в другом окне:

```powershell
.\start-admin.ps1
```

Админка: [http://127.0.0.1:8501](http://127.0.0.1:8501)

Если скрипты блокируются политикой PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Структура

```
лисенок/
├── main.py              # FastAPI: сайт + API
├── admin.py             # Streamlit-админка
├── database.py          # модели и подключение к БД
├── schemas.py           # схемы ответов API
├── seed.py              # демо-товары и опции
├── config.py            # настройки из .env
├── docker-compose.yml   # PostgreSQL для сервера
├── static/index.html    # витрина
└── requirements.txt
```

## База данных

Локально по умолчанию используется SQLite (`lisenok.db`), чтобы сайт открывался без установки PostgreSQL.

На VDS скопируйте `.env.example` в `.env` и укажите PostgreSQL:

```env
DATABASE_URL=postgresql://lisenok:password@localhost:5432/lisenok_db
```

Поднять Postgres:

```bash
docker compose up -d db
```

## Фон леса

Положите файл `static/forest-bg.mp4` — живое видео включится само. Пока файла нет, работает статичный лесной фон.

## Когда появится VDS

1. Установить Python 3.11+, nginx, (опционально) Docker.
2. Скопировать проект, создать `.venv`, установить `requirements.txt`.
3. Заполнить `.env` с PostgreSQL.
4. Запустить API через systemd или `uvicorn main:app --host 127.0.0.1 --port 8000`.
5. Проксировать домен на порт 8000 через nginx.
6. Админку держать на localhost или закрыть паролем / VPN.

Точные команды под ваш сервер пропишем, когда будут доступы.

## API

| Метод | Путь | Назначение |
| --- | --- | --- |
| GET | `/api/health` | проверка сервера |
| GET | `/api/catalog` | активные товары |
| GET | `/api/constructor-options` | опции конструктора |
| POST | `/api/inquiry` | заявка с сайта |
