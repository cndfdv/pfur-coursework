# ArXiv Semantic Search — Project Instructions

## Что нужно сделать

Полнофункциональный semantic search по научным статьям arXiv с красивым веб-интерфейсом и несколькими NoSQL БД.

---

## Стек

- **Qdrant** — векторная БД, хранит эмбеддинги абстрактов
- **Redis** — кэш запросов (ключ = текст запроса, значение = список id результатов)
- **ClickHouse** — аналитика: логи запросов, топ поисковых фраз, статистика по годам/категориям
- **MongoDB** — метаданные статей (title, authors, year, categories, abstract, arxiv_id)
- **FastAPI** — бэкенд
- **React (Vite)** — фронтенд
- **sentence-transformers** — модель `all-MiniLM-L6-v2` для эмбеддингов (лёгкая, быстрая)

---

## Структура проекта

```
arxiv-search/
├── docker-compose.yml
├── CLAUDE.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── db/
│   │   ├── qdrant_client.py
│   │   ├── redis_client.py
│   │   ├── clickhouse_client.py
│   │   └── mongo_client.py
│   └── scripts/
│       └── load_data.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── App.jsx
        ├── main.jsx
        └── components/
            ├── SearchBar.jsx
            ├── ResultCard.jsx
            ├── StatsPanel.jsx
            └── Loader.jsx
```

---

## docker-compose.yml

Подними следующие сервисы:

```yaml
version: "3.9"
services:
  qdrant:
    image: qdrant/qdrant
    ports: ["6333:6333"]
    volumes: ["qdrant_data:/qdrant/storage"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  clickhouse:
    image: clickhouse/clickhouse-server
    ports: ["8123:8123", "9000:9000"]
    volumes: ["clickhouse_data:/var/lib/clickhouse"]

  mongo:
    image: mongo:7
    ports: ["27017:27017"]
    volumes: ["mongo_data:/data/db"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [qdrant, redis, clickhouse, mongo]
    environment:
      - QDRANT_HOST=qdrant
      - REDIS_HOST=redis
      - CLICKHOUSE_HOST=clickhouse
      - MONGO_HOST=mongo

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]

volumes:
  qdrant_data:
  clickhouse_data:
  mongo_data:
```

---

## Данные

Используй датасет **arxiv-metadata-oai-snapshot** с Kaggle (JSON Lines).
Если нет доступа — скачай альтернативу:

```bash
pip install kaggle
kaggle datasets download -d Cornell-University/arxiv
```

Или используй публичный семпл: https://github.com/arXiv/arxiv-public-datasets

Скрипт `backend/scripts/load_data.py` должен:
1. Читать JSON Lines файл
2. Взять **5000–10000 статей** категорий `cs.AI`, `cs.LG`, `cs.CV` (фильтр по полю `categories`)
3. Для каждой статьи:
   - Сохранить метаданные в **MongoDB** (коллекция `articles`)
   - Сгенерировать эмбеддинг абстракта через `SentenceTransformer("all-MiniLM-L6-v2")`
   - Сохранить вектор в **Qdrant** (коллекция `arxiv`, размер вектора 384)
4. Создать таблицу в **ClickHouse**:
   ```sql
   CREATE TABLE IF NOT EXISTS search_logs (
     query String,
     results_count UInt32,
     timestamp DateTime DEFAULT now()
   ) ENGINE = MergeTree() ORDER BY timestamp
   ```
5. Вывести прогресс батчами по 100 статей

---

## Backend (FastAPI)

### Эндпоинты

**GET /api/search?q={query}&limit={10}**
1. Проверить Redis кэш по ключу `search:{query}`
2. Если нет — эмбеддить запрос, искать в Qdrant top-K
3. Достать метаданные из MongoDB по `arxiv_id`
4. Записать в Redis с TTL 1 час
5. Залогировать в ClickHouse (query, results_count, timestamp)
6. Вернуть результаты

Формат ответа:
```json
{
  "results": [
    {
      "arxiv_id": "2301.00001",
      "title": "...",
      "authors": ["..."],
      "year": 2023,
      "categories": ["cs.AI"],
      "abstract": "...",
      "score": 0.87,
      "cached": false
    }
  ],
  "total": 10,
  "cached": false,
  "query_time_ms": 45
}
```

**GET /api/stats**

Возвращает из ClickHouse + MongoDB:
```json
{
  "total_articles": 8432,
  "top_queries": [{"query": "transformer", "count": 12}, ...],
  "articles_by_year": [{"year": 2023, "count": 1200}, ...],
  "articles_by_category": [{"category": "cs.AI", "count": 3400}, ...]
}
```

**GET /api/health** — статусы всех БД

---

## Frontend (React + Vite)

### Дизайн

Тёмная тема. Минималистично, чисто. Вдохновение — Perplexity AI + arXiv.

**Цветовая палитра:**
- Background: `#0f1117`
- Surface: `#1a1d27`
- Border: `#2a2d3e`
- Accent: `#6366f1` (indigo)
- Text primary: `#e2e8f0`
- Text secondary: `#94a3b8`
- Score badge: зелёный градиент по значению (0.5→1.0)

**Используй:** Tailwind CSS (через CDN в index.html или через npm)

### Страницы и компоненты

**App.jsx** — два таба: "Search" и "Analytics"

**SearchBar.jsx**
- Большая строка поиска по центру при пустом состоянии (как Google)
- После поиска сдвигается наверх
- Плейсхолдер: `"e.g. attention mechanism for image segmentation"`
- Кнопка поиска + Enter
- Показывать badge "cached" если ответ из Redis

**ResultCard.jsx**
- Карточка статьи: title (кликабельный → arxiv.org/abs/{id}), авторы, год, категории как теги, первые 300 символов абстракта с кнопкой "Show more", score badge справа
- Hover эффект с подсветкой border

**StatsPanel.jsx** — таб Analytics:
- Число статей в базе
- Top-10 запросов как список
- Bar chart по годам (можно через простой CSS или recharts)
- Распределение по категориям

**Loader.jsx** — анимированный скелетон пока грузится

---

## Запуск

После того как всё написано:

```bash
# Поднять БД
docker-compose up -d qdrant redis clickhouse mongo

# Установить зависимости бэка
cd backend && pip install -r requirements.txt

# Загрузить данные (запустить один раз)
python scripts/load_data.py --file /path/to/arxiv-metadata.json --limit 8000

# Запустить бэкенд
uvicorn main:app --reload --port 8000

# Запустить фронт
cd frontend && npm install && npm run dev
```

Или всё через docker-compose если добавить команды запуска в Dockerfile'ы.

---

## requirements.txt

```
fastapi
uvicorn
sentence-transformers
qdrant-client
redis
clickhouse-connect
pymongo
python-dotenv
tqdm
pydantic
```

---

## Важные детали

- CORS на бэке должен разрешать `http://localhost:5173`
- Qdrant коллекцию создавать при старте если не существует (upsert-safe)
- Redis ключи: `search:{запрос в нижнем регистре без лишних пробелов}`
- MongoDB индекс по полю `arxiv_id`
- В ClickHouse использовать `clickhouse-connect`, не `clickhouse-driver`
- Если датасета нет — сгенерировать 500 фейковых статей через Faker для демонстрации структуры
