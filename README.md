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

---

## Структура репозитория

```
nosql/
├── environment.yml       # conda/mamba окружение
├── README.md             # этот файл
└── lab_1_redis/
    ├── docker-compose.yml
    ├── main.ipynb
    └── README.md
```
