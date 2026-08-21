# Карта файлов проекта

Ниже краткое объяснение по файлам: что это за файл и зачем он нужен.

## Корень проекта

### `CLAUDE.md`

Техническое задание проекта: требования к стеку, API, структуре и данным.

### `README.md`

Краткая пользовательская документация: как запустить проект, какие есть endpoint'ы и как устроен стек.

### `speech.md`

Текст выступления под презентацию.

### `arxiv_search.pptx`

Готовая презентация проекта.

### `build_pptx.py`

Python-скрипт, который программно генерирует презентацию `.pptx`.

Это отдельная утилита для подготовки слайдов, а не часть runtime приложения.

### `docker-compose.yml`

Главный инфраструктурный файл проекта.

Поднимает все контейнеры и задаёт их связи.

## Backend

### `backend/Dockerfile`

Собирает backend-образ:

- берёт `python:3.11-slim`
- ставит системные зависимости
- ставит Python-библиотеки
- копирует код
- запускает `uvicorn`

### `backend/requirements.txt`

Список Python-зависимостей:

- `fastapi`
- `uvicorn`
- `sentence-transformers`
- `qdrant-client`
- `redis`
- `clickhouse-connect`
- `pymongo`
- `python-dotenv`
- `tqdm`
- `faker`

### `backend/config.py`

Центральная конфигурация backend.

### `backend/main.py`

Главная логика API:

- старт приложения
- загрузка модели
- endpoint'ы `/api/search`, `/api/stats`, `/api/health`

### `backend/db/__init__.py`

Пустой служебный файл пакета Python, чтобы каталог `db` был импортируемым модулем.

### `backend/db/qdrant_client.py`

Весь код общения с Qdrant.

### `backend/db/mongo_client.py`

Весь код общения с MongoDB.

### `backend/db/redis_client.py`

Весь код общения с Redis и кэшированием.

### `backend/db/clickhouse_client.py`

Весь код общения с ClickHouse и аналитикой логов.

### `backend/scripts/__init__.py`

Служебный файл пакета для каталога `scripts`.

### `backend/scripts/load_data.py`

Скрипт первоначальной загрузки данных.

Поддерживает:

- реальный JSONL-файл arXiv
- fake-режим
- `--force`

## Frontend

### `frontend/Dockerfile`

Собирает frontend-контейнер на `node:20-alpine` и запускает `vite`.

### `frontend/package.json`

NPM-конфигурация проекта frontend.

### `frontend/vite.config.js`

Настройка Vite dev server и proxy для `/api`.

### `frontend/tailwind.config.js`

Конфигурация Tailwind и дизайн-токены проекта.

### `frontend/postcss.config.js`

Подключение плагинов `tailwindcss` и `autoprefixer`.

### `frontend/index.html`

Базовый HTML-шаблон frontend-приложения.

### `frontend/src/main.jsx`

Точка входа React.

### `frontend/src/App.jsx`

Корневой UI-компонент.

### `frontend/src/api.js`

Функции для работы с backend API.

### `frontend/src/index.css`

Глобальные стили, тема и skeleton-анимация.

### `frontend/src/components/SearchBar.jsx`

Компонент строки поиска.

### `frontend/src/components/ResultCard.jsx`

Компонент карточки статьи.

### `frontend/src/components/StatsPanel.jsx`

Компонент вкладки аналитики.

### `frontend/src/components/Loader.jsx`

Компонент skeleton-загрузки.

## Как читать код по порядку

Если нужно быстро понять проект, лучше идти так:

1. `docker-compose.yml`
2. `backend/main.py`
3. `backend/db/*.py`
4. `backend/scripts/load_data.py`
5. `frontend/src/App.jsx`
6. `frontend/src/api.js`
7. `frontend/src/components/*.jsx`

Такой порядок отражает реальный жизненный цикл проекта:

- сначала инфраструктура
- потом backend-логика
- потом загрузка данных
- потом интерфейс
