# Развертывание сервиса аналитики

## Шаги для запуска

1. **Соберите и запустите контейнер:**
   ```bash
   docker-compose build analytics
   docker-compose up -d analytics
   ```

2. **Проверьте логи:**
   ```bash
   docker logs -f maks-koits-cv-analytics
   ```

3. **Проверьте работу:**
   - Откройте https://analytics.maks-koits.cv/health (должен вернуть `{"status": "ok"}`)
   - Откройте https://analytics.maks-koits.cv/stats (должен показать интерфейс статистики)

4. **Проверьте трекинг:**
   - Откройте https://maks-koits.cv
   - Откройте https://analytics.maks-koits.cv/stats - должно появиться новое посещение

## Структура файлов

```
analytics/
├── app.py              # Основное Flask приложение
├── Dockerfile          # Docker образ
├── requirements.txt    # Python зависимости
├── tracker.js          # JavaScript трекер (копируется в maks-koits.cv/js/)
├── README.md           # Документация
├── USAGE.md            # Инструкция по использованию
└── DEPLOY.md           # Инструкция по развертыванию
```

## Переменные окружения

Настраиваются в `docker-compose.yaml`:

- `DATABASE_PATH` - путь к SQLite БД (по умолчанию: `/data/analytics.db`)
- `PORT` - порт Flask (по умолчанию: `5000`)
- `LOG_LEVEL` - уровень логирования (по умолчанию: `INFO`)

## Данные

База данных SQLite хранится в `/app/analytics_data/analytics.db` на хосте.

Для просмотра данных можно использовать:
```bash
# Установить sqlite3 на хосте
apt-get install sqlite3

# Подключиться к БД
sqlite3 /app/analytics_data/analytics.db

# Примеры запросов:
SELECT COUNT(*) FROM visits;
SELECT country, COUNT(*) FROM visits GROUP BY country ORDER BY COUNT(*) DESC;
```

## Обновление

При изменении кода:
```bash
docker-compose build analytics
docker-compose up -d analytics
```

## Устранение проблем

1. **Трекер не отправляет данные:**
   - Проверьте консоль браузера (F12) на ошибки
   - Проверьте CORS настройки
   - Проверьте доступность https://analytics.maks-koits.cv/track

2. **Не определяется страна:**
   - Проверьте доступность ip-api.com из контейнера
   - Проверьте логи на ошибки API
   - Возможно превышен лимит 45 запросов/минуту

3. **Медленные запросы:**
   - Проверьте индексы в БД: `sqlite3 /app/analytics_data/analytics.db ".indices visits"`
   - При большом объеме данных рассмотрите переход на PostgreSQL

## Мониторинг ресурсов

Проверка использования ресурсов:
```bash
docker stats maks-koits-cv-analytics
```

Ожидаемое потребление:
- RAM: ~50-100MB
- CPU: минимальное (только при запросах)
- Disk: зависит от количества посещений (~1MB на 1000 посещений)
