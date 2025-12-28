import os
import logging
import time
from typing import Optional

import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import NetworkError, RetryAfter, TimedOut


API_URL = "https://fucking-great-advice.ru/api/random"


logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def fetch_advice_text() -> Optional[str]:
    try:
        logger.info("Fetching advice from: %s", API_URL)
        response = requests.get(API_URL, timeout=10)
        logger.info("Response status: %s", response.status_code)
        logger.info("Response headers: %s", dict(response.headers))
        logger.info("Response content: %s", response.text[:200])
        
        response.raise_for_status()
        data = response.json()
        logger.info("Parsed JSON: %s", data)
        
        text = data.get("text")
        logger.info("Extracted text: %s", text)
        
        if not isinstance(text, str) or not text.strip():
            logger.warning("Text is empty or not a string: %s", text)
            return None
        return text.strip()
    except requests.exceptions.RequestException as exc:
        logger.error("Request failed: %s", exc)
        return None
    except ValueError as exc:
        logger.error("JSON decode failed: %s", exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        return None


async def send_advice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = fetch_advice_text()

    reply_kwargs = {}
    try:
        if update.effective_chat and getattr(update.effective_chat, "type", "") == "private":
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton("/advice"), KeyboardButton("/sovet")]],
                resize_keyboard=True,
                one_time_keyboard=False,
            )
            reply_kwargs["reply_markup"] = keyboard
    except Exception:
        pass

    if text is None:
        await update.effective_chat.send_message(
            "Не удалось получить совет. Попробуйте ещё раз позже.",
            **reply_kwargs,
        )
        return
    await update.effective_chat.send_message(text, **reply_kwargs)


async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка упоминаний бота в групповых чатах"""
    # Получаем информацию о боте
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    bot_username_lower = bot_username.lower()
    
    # Проверяем, упоминается ли бот в сообщении
    if update.message and update.message.text:
        message_text = update.message.text.lower()
        if f"@{bot_username_lower}" in message_text or f"/start@{bot_username_lower}" in message_text:
            await send_advice(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_advice(update, context)


async def advice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /advice для получения совета"""
    await send_advice(update, context)


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Отсутствует TELEGRAM_BOT_TOKEN в переменных окружения")

    max_retries = 10
    retry_delay = 5  # Начальная задержка в секундах
    max_delay = 300  # Максимальная задержка (5 минут)
    
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Запуск бота (попытка {retry_count + 1}/{max_retries})...")
            
            # Настройка Application с улучшенными параметрами для работы в контейнере
            application = (
                Application.builder()
                .token(token)
                .connect_timeout(30.0)  # Увеличенный таймаут подключения
                .read_timeout(30.0)     # Увеличенный таймаут чтения
                .write_timeout(30.0)     # Увеличенный таймаут записи
                .pool_timeout(30.0)      # Таймаут для пула соединений
                .build()
            )

            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("advice", advice_command))
            application.add_handler(CommandHandler("sovet", advice_command))
            # Любое текстовое сообщение вызывает получение совета (для личных чатов)
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, send_advice))
            # Обработка упоминаний бота в групповых чатах
            application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_mention))

            # Добавляем обработчик ошибок сети
            async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
                """Обработчик ошибок"""
                logger.error(f"Ошибка при обработке обновления: {context.error}")
                
                if isinstance(context.error, NetworkError):
                    logger.warning("Обнаружена сетевая ошибка, но бот продолжит работу")
                elif isinstance(context.error, RetryAfter):
                    logger.warning(f"Превышен лимит запросов, ожидание {context.error.retry_after} секунд")
                elif isinstance(context.error, TimedOut):
                    logger.warning("Таймаут запроса")

            application.add_error_handler(error_handler)
            
            logger.info("Бот успешно запущен")
            application.run_polling(
                close_loop=False,
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
            # Если дошли сюда, значит бот остановился нормально
            break
            
        except (NetworkError, ConnectionError, OSError) as e:
            retry_count += 1
            logger.error(f"Сетевая ошибка (попытка {retry_count}/{max_retries}): {e}")
            
            if retry_count >= max_retries:
                logger.critical(f"Достигнуто максимальное количество попыток ({max_retries}). Остановка бота.")
                raise
            
            # Экспоненциальная задержка с ограничением
            delay = min(retry_delay * (2 ** (retry_count - 1)), max_delay)
            logger.info(f"Повторная попытка через {delay} секунд...")
            time.sleep(delay)
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки (Ctrl+C)")
            break
            
        except Exception as e:
            retry_count += 1
            logger.error(f"Неожиданная ошибка (попытка {retry_count}/{max_retries}): {e}", exc_info=True)
            
            if retry_count >= max_retries:
                logger.critical(f"Достигнуто максимальное количество попыток ({max_retries}). Остановка бота.")
                raise
            
            delay = min(retry_delay * (2 ** (retry_count - 1)), max_delay)
            logger.info(f"Повторная попытка через {delay} секунд...")
            time.sleep(delay)


def test_api():
    """Тестовая функция для проверки API"""
    print("Testing API...")
    text = fetch_advice_text()
    if text:
        print(f"Success! Got text: {text}")
    else:
        print("Failed to get text")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_api()
    else:
        main()



