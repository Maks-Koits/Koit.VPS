# Очистка базы данных аналитики

## Способ 1: Через SQL команду (рекомендуется)

```bash
# На сервере
sqlite3 /app/analytics_data/analytics.db "DELETE FROM visits;"
```

Или через docker:
```bash
docker exec maks-koits-cv-analytics sqlite3 /data/analytics.db "DELETE FROM visits;"
```

## Способ 2: Удалить файл БД (будет создан заново)

```bash
# На сервере
rm -f /app/analytics_data/analytics.db

# Перезапустить контейнер для создания новой БД
docker-compose restart analytics
```

## Способ 3: Очистить и сбросить автоинкремент

```bash
sqlite3 /app/analytics_data/analytics.db "DELETE FROM visits; DELETE FROM sqlite_sequence WHERE name='visits';"
```

## Способ 4: Очистить старые записи (старше N дней)

```bash
# Удалить записи старше 30 дней
sqlite3 /app/analytics_data/analytics.db "DELETE FROM visits WHERE timestamp < datetime('now', '-30 days');"
```

## Способ 5: Через Python скрипт

Создайте файл `clear_db.py`:
```python
import sqlite3
import os

db_path = os.environ.get('DATABASE_PATH', '/data/analytics.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('DELETE FROM visits')
conn.commit()
conn.close()
print("База данных очищена!")
```

Запуск:
```bash
docker exec maks-koits-cv-analytics python /app/clear_db.py
```

## Проверка количества записей

```bash
sqlite3 /app/analytics_data/analytics.db "SELECT COUNT(*) FROM visits;"
```

Или через docker:
```bash
docker exec maks-koits-cv-analytics sqlite3 /data/analytics.db "SELECT COUNT(*) FROM visits;"
```

## Резервное копирование перед очисткой

```bash
# Создать резервную копию
cp /app/analytics_data/analytics.db /app/analytics_data/analytics.db.backup.$(date +%Y%m%d)

# Очистить БД
sqlite3 /app/analytics_data/analytics.db "DELETE FROM visits;"
```

## Восстановление из резервной копии

```bash
cp /app/analytics_data/analytics.db.backup.20260210 /app/analytics_data/analytics.db
```
