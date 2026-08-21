# ArXiv Semantic Search

Полнофункциональный semantic search по статьям arXiv на четырёх NoSQL БД.

**Стек:** Qdrant (векторы) · Redis (кэш) · ClickHouse (аналитика) · MongoDB (метаданные) · FastAPI · React/Vite · `sentence-transformers` (`all-MiniLM-L6-v2`).

---

## Быстрый старт (одной командой)

```bash
docker compose up --build
```

Compose поднимет:

1. Четыре БД (Qdrant, Redis, ClickHouse, Mongo) с healthcheck'ами
2. **Loader** — one-shot сервис, который дожидается БД, скачивает модель, генерирует 500 демо-статей через Faker и заливает в Mongo + Qdrant. Если данные уже загружены — skip.
3. **Backend** (FastAPI) на http://localhost:8000 (ждёт, пока loader завершится успешно)
4. **Frontend** (Vite dev) на http://localhost:5173

Первый запуск займёт ~2–5 минут: сборка образов + скачивание модели `all-MiniLM-L6-v2` (~90 MB, кэшируется в volume `hf_cache`).

**Повторные `docker compose up`** стартуют мгновенно: loader видит непустой Qdrant и выходит, модель уже в кэше.

### Настроить объём демо-данных

```bash
LOAD_COUNT=2000 docker compose up --build
```

### Загрузить реальный датасет arXiv вместо fake

```bash
# 1. Поднять всё как обычно (с fake)
docker compose up -d

# 2. Скачать датасет на хост (Kaggle)
kaggle datasets download -d Cornell-University/arxiv
unzip arxiv.zip

# 3. Скопировать внутрь контейнера и перегрузить
docker cp arxiv-metadata-oai-snapshot.json arxiv_backend:/tmp/arxiv.json
docker compose exec backend python scripts/load_data.py \
  --file /tmp/arxiv.json --limit 8000 --force
```

---

## Эндпоинты

| Method | Path | Описание |
|--------|------|----------|
| GET | `/api/search?q=...&limit=10` | Семантический поиск + Redis-кэш + лог в ClickHouse |
| GET | `/api/stats` | Метрики: всего статей, top queries, распределение по годам/категориям |
| GET | `/api/health` | Живость всех четырёх БД |

Swagger: http://localhost:8000/docs

---

## Подробная документация по коду

Если нужна не инструкция по запуску, а именно объяснение архитектуры и файлов проекта, смотри папку [`docs/`](./docs/README.md):

- `docs/01-overview.md` — общий обзор проекта
- `docs/02-infrastructure.md` — Docker, контейнеры, загрузка данных
- `docs/03-backend.md` — FastAPI, поиск, БД
- `docs/04-frontend.md` — React-интерфейс
- `docs/05-file-map.md` — карта файлов проекта

---

## Как работает поиск

1. Приходит `GET /api/search?q=...`
2. Проверяется Redis (ключ `search:{lowercased_query}`, TTL 1ч)
3. При промахе — текст эмбеддится в 384-мерный вектор и ищется top-K в Qdrant
4. По найденным `arxiv_id` достаются метаданные из MongoDB
5. Результат пишется в Redis и логируется строкой в ClickHouse (`search_logs`)
6. Возвращается JSON с `query_time_ms` и флагом `cached`

---

## Структура

```
.
├── docker-compose.yml       # всё поднимается одной командой
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config.py            # настройки через env
│   ├── main.py              # FastAPI + CORS + lifespan
│   ├── db/
│   │   ├── qdrant_client.py
│   │   ├── redis_client.py
│   │   ├── clickhouse_client.py
│   │   └── mongo_client.py
│   └── scripts/
│       └── load_data.py     # --file, --fake N, --force
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── api.js
        ├── index.css
        └── components/
            ├── SearchBar.jsx
            ├── ResultCard.jsx
            ├── StatsPanel.jsx
            └── Loader.jsx
```

---

## Локальная разработка без Docker (опционально)

Если нужно дебажить бэк без пересборки образа:

```bash
# БД — всё ещё из compose
docker compose up -d qdrant redis clickhouse mongo

# Бэк локально
cd backend
pip install -r requirements.txt
python scripts/load_data.py --fake 500
uvicorn main:app --reload --port 8000

# Фронт локально
cd frontend
npm install
npm run dev
```

---

## Сервисы и порты

| Сервис     | Порт          |
|------------|---------------|
| Frontend   | 5173          |
| Backend    | 8000          |
| Qdrant     | 6333          |
| Redis      | 6379          |
| ClickHouse | 8123, 9000    |
| MongoDB    | 27017         |

---

## Остановка и очистка

```bash
docker compose down              # стоп
docker compose down -v           # стоп + снести volumes (данные, кэш модели)
```
