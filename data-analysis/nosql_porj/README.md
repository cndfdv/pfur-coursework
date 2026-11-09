# ArXiv Semantic Search

Учебный семантический поиск на четырёх NoSQL БД. По умолчанию загружаются
сгенерированные демо-статьи; реальные записи arXiv можно импортировать отдельно.

**Стек:** Qdrant (векторы) · Redis (кэш) · ClickHouse (аналитика) · MongoDB (метаданные) · FastAPI · React/Vite · `sentence-transformers` (`all-MiniLM-L6-v2`).

---

## Быстрый старт (одной командой)

```bash
docker compose up --build
```

Compose поднимет:

1. Четыре БД (Qdrant, Redis, ClickHouse, Mongo). В Compose healthcheck настроен для Redis, ClickHouse и Mongo; для Qdrant healthcheck не задан.
2. **Loader** — one-shot сервис, который загружает модель и генерирует 500 демо-статей через Faker для MongoDB и Qdrant. Если в Qdrant уже есть точки, загрузчик пропускает импорт.
3. **Backend** (FastAPI) на http://localhost:8000 (ждёт, пока loader завершится успешно)
4. **Frontend** (Vite dev) на http://localhost:5173

Первый запуск собирает образы и скачивает модель `all-MiniLM-L6-v2` в volume `hf_cache`.

При повторном запуске с сохранёнными volumes загрузчик пропустит импорт при непустом Qdrant. Backend всё равно загружает модель при старте.

### Настроить объём демо-данных

```bash
LOAD_COUNT=2000 docker compose up --build
```

### Загрузить реальные записи arXiv

Загрузчик принимает JSON Lines (один JSON-объект на строку), а не JSON-массив.
Сначала запустите Compose и дождитесь готовности backend. Затем поместите файл
в контейнер и запустите загрузчик с `--force`, чтобы выполнить импорт даже при
непустом Qdrant:

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
2. Проверяется Redis (ключ `search:{нормализованный_запрос}`, пробелы сводятся к одному, регистр приводится к нижнему; TTL 1 ч)
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

## Сервисы и порты

| Сервис     | Порт          |
|------------|---------------|
| Frontend   | 5173          |
| Backend    | 8000          |
| Qdrant     | 6333 (внутри сети Compose) |
| Redis      | 6379 (внутри сети Compose) |
| ClickHouse | 8123, 9000 (внутри сети Compose) |
| MongoDB    | 27017 (внутри сети Compose) |

На хост проброшены порты Frontend `5173` и Backend `8000`; порты баз данных в Compose не опубликованы.

---

## Остановка и очистка

```bash
docker compose down              # стоп
docker compose down -v           # стоп + снести volumes (данные, кэш модели)
```
