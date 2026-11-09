# Лабораторная работа 6: async I/O

## Запуск

```bash
pip install -r requirements.txt
python main.py
```

Скрипт формирует 100 URL для `jsonplaceholder.typicode.com` (`/comments/1`–`/comments/100`) и измеряет два способа запроса:

- `fetch_sync` — синхронно через `requests`, один URL за раз.
- `main_async` — конкурентно через `aiohttp`, `asyncio.gather` и `asyncio.Semaphore`.

Ошибки запросов записываются в `app.log`. При сетевой ошибке или таймауте для соответствующего URL возвращается `{}`. Для async-части требуется `aiohttp`; если модуль не установлен, скрипт пропускает её. Запуск требует доступа к сети.

Тесты находятся в `tests/test_lab6.py`. Из каталога этой лабораторной их можно запустить командой `python -m pytest`.
