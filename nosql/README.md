# NoSQL — Лабораторные работы

## Требования

- [Miniforge / Mamba](https://github.com/conda-forge/miniforge) (или Miniconda + conda)
- [Docker](https://docs.docker.com/get-docker/) + Docker Compose

---

## Первичная настройка (один раз)

```bash
mamba env create -f environment.yml
```

---

## Лабораторные работы

### Лабораторная 1 — Redis

```bash
cd lab_1_redis
docker compose up -d      # запустить Redis 7 на localhost:6379
```

Открыть [lab_1_redis/main.ipynb](lab_1_redis/main.ipynb), выбрать ядро **Python (nosql)**, выполнить ячейки по порядку.

Остановить Redis: `docker compose down`

Подробнее: [lab_1_redis/README.md](lab_1_redis/README.md)

### Лабораторная 2 — кэш

`lab_2_cache/` содержит ноутбук с проверками класса `Cache`, реализацию `cache.py`, постановку и пояснение.

### Лабораторная 3 — WAL

`lab_3_wal/` содержит ноутбук, реализацию WAL-кэша `wal_cache.py`, постановку и пояснение.

### Лабораторная 4 — SSTable

`lab_4_sstable/` содержит ноутбук, реализацию `sstable.py`, файл данных `data.sst`, постановку и пояснение.

---

## Структура репозитория

```
nosql/
├── environment.yml
├── lab_1_redis/
├── lab_2_cache/
├── lab_3_wal/
└── lab_4_sstable/
```
