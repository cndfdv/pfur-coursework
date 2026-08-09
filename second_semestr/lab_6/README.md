# Лабораторная работа 6: async I/O

## Запуск

```bash
pip install -r requirements.txt
python main.py
```

Скрипт делает 100 запросов к `jsonplaceholder.typicode.com` двумя способами:

- `fetch_sync` — синхронно через `requests`, один URL за раз.
- `main_async` — конкурентно через `aiohttp`, `asyncio.gather` и `asyncio.Semaphore`.

Ошибки сети и таймауты пишутся в `app.log`, а вместо падения функция возвращает пустой словарь `{}` для проблемного URL.
