## Telegram Advice Bot

Бот для Telegram, который по команде получает рандомный совет по API и отправляет только текст совета в чат.

- Источник советов: `http://fucking-great-advice.ru/api/random`

### Требования
- Python 3.9+

### Установка
1. Клонируйте проект или скопируйте файлы в папку.
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создайте файл `.env` по примеру:
   ```bash
   copy .env.example .env   # в PowerShell: cp .env.example .env
   ```
   И укажите токен Telegram бота.

### Переменные окружения
Создайте файл `.env` в корне проекта:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
``` 

### Запуск
```bash
python bot.py
```

### Запуск в Docker
Собрать образ:
```bash
docker build -t advice-bot:latest .
```

Запустить контейнер, передав токен:
```bash
docker run -d -e TELEGRAM_BOT_TOKEN=ваш_токен_бота --name advice-bot advice-bot:latest
```

Либо через файл окружения:
```bash
echo TELEGRAM_BOT_TOKEN=ваш_токен_бота > .env
docker run -d --env-file .env --name advice-bot advice-bot:latest
```

### Использование
- Напишите боту любое сообщение или команду `/start`, `/sovet`, `/advice` — бот сходит в API и ответит текстом из поля `text`.

### Примечания
- Если API вернул ошибку или неожиданный формат, бот отправит короткое сообщение об ошибке.
