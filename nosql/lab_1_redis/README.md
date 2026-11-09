# Лабораторная работа 1: Redis

## Запуск окружения

### 1. Поднять Redis в Docker

```bash
cd lab_1_redis
docker compose up -d
```

Redis будет доступен на `localhost:6379`. Остановить: `docker compose down`.

### 2. Запустить ноутбук

Откройте [main.ipynb](main.ipynb) в Jupyter или VS Code и выполните ячейки по порядку. Ноутбук использует пакет `redis`; окружение `nosql` с ним описано в [`../environment.yml`](../environment.yml).

---

## Структура ноутбука

| Раздел | Что делается |
|---|---|
| Подключение | `redis.Redis(host='localhost', port=6379)` — проверка через `ping()` |
| 2.1.1 Строки + TTL | SET / GET / EXPIRE / TTL / DEL |
| 2.1.2 Хэши | HSET / HGET / HGETALL / HINCRBY / HDEL |
| 2.1.3 Списки | LPUSH / LRANGE / LINDEX / RPOP / LTRIM |
| 2.1.4 Множества | SADD / SMEMBERS / SISMEMBER / SREM / SCARD / SINTER |
| 2.2 Чат Pub/Sub | Публикация / подписка, история, threading |

---

## Ключевые концепции

### TTL (Time To Live)
- `TTL key` возвращает `-1` — ключ есть, срок не задан
- `TTL key` возвращает `-2` — ключ не существует
- `EXPIRE key 30` — ключ исчезнет через 30 секунд

### Хэши vs Строки
Хэш предпочтительнее строки когда объект имеет несколько полей: можно обновить одно поле (`HSET user:1 age 26`) не перезаписывая весь объект.

### Список: направление имеет значение
- `LPUSH` кладёт в голову (левый конец)
- `RPOP` забирает из хвоста (правый конец)
- `LPUSH` + `RPOP` = очередь FIFO (первый пришёл — первым ушёл)
- `LTRIM 0 N-1` — удобный паттерн «хранить последние N записей»

### Множество vs Список
- Set: уникальные элементы, нет порядка — хорошо для тегов, подписчиков
- List: допускает дубликаты, порядок вставки сохраняется — хорошо для лент и очередей
- `SINTER key1 key2` — общие элементы двух множеств (например, общие теги постов)

### Pub/Sub и Чат
- Издатель: `r.publish(CHANNEL, json_message)`
- Подписчик: `pubsub = r.pubsub(); pubsub.subscribe(CHANNEL); pubsub.listen()`
- Подписчик слушает в отдельном потоке (`threading.Thread`), чтобы не блокировать отправку
- История хранится в Redis List `RUDN_CHAT_HISTORY`; `LTRIM` держит не более 20 сообщений

---

## Файлы

```
lab_1_redis/
├── docker-compose.yml   # Redis 7 на порту 6379
├── main.ipynb           # Весь код лабораторной
└── README.md            # Этот файл
```
