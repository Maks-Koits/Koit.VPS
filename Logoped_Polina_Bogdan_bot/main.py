from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import os

API_TOKEN = os.environ['API_TOKEN']

# API_TOKEN: str = '6092736622:AAE-M9nWHVkY5_8qgWAkhOpCd0rB6g9YCak'

# погнали ;) Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()

# Создаем объекты инлайн-кнопок
url_button_1: InlineKeyboardButton = InlineKeyboardButton(
    text='Записаться на индивидуальное занятие',
    url='https://t.me/logoped_polinabogdan')
url_button_2: InlineKeyboardButton = InlineKeyboardButton(
    text='Развивающие занятия на YouTube',
    url=f'https://www.youtube.com/@logoped_polinabogdan')
url_button_3: InlineKeyboardButton = InlineKeyboardButton(
    text='Развивающие занятия в TikTok',
    url=f'https://www.tiktok.com/@logoped.polinabogdan?_t=8eJqIVhg4Sj&_r=1')
url_button_4: InlineKeyboardButton = InlineKeyboardButton(
    text='Мой аккаунт в Instagram',
    url=f'https://www.instagram.com/logoped_polinabogdan/')

# Создаем объект инлайн-клавиатуры
keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[url_button_1],
                     [url_button_2],
                     [url_button_3],
                     [url_button_4]
                     ])


# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру c url-кнопками
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text='Чем я могу Вам помочь?',
                         reply_markup=keyboard)


# Этот хэндлер будет срабатывать на команду "/other"
# и отправлять в чат клавиатуру c url-кнопками
@dp.message(Command(commands='other'))
async def process_other_command(message: Message):
    await message.answer(text='Чем я могу Вам помочь?',
                         reply_markup=keyboard)


if __name__ == '__main__':
    dp.run_polling(bot)
