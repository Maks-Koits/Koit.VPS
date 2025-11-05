import os
import logging
from typing import Optional

import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


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

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("advice", advice_command))
    application.add_handler(CommandHandler("sovet", advice_command))
    # Любое текстовое сообщение вызывает получение совета (для личных чатов)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, send_advice))
    # Обработка упоминаний бота в групповых чатах
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_mention))

    application.run_polling(close_loop=False)


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



