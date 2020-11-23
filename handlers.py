# import asyncio
# import datetime

from aiogram import types
# from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery)
# from aiogram.utils.callback_data import CallbackData

import database
# import states
from config import admin_id
from load_all import dp, bot, _

db = database.DBCommands()

# Для команды /start есть специальный фильтр, который можно тут использовать
@dp.message_handler(CommandStart())
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    user = await db.add_new_user(referral=referral)
    id = user.id
    count_users = await db.count_users()

    # Отдадим пользователю клавиатуру с выбором языков
    languages_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
            [
            [
                    InlineKeyboardButton(text="O'zbek 🇺🇿", callback_data="lang_uz")],
            ]
        ]
    )

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"

    # Для многоязычности, все тексты, передаваемые пользователю должны передаваться в функцию "_"
    # Вместо "текст" передаем _("текст")

    text = _("Приветствую вас!!\n"
             "Сейчас в базе {count_users} человек!\n"
             "\n"
             "Ваша реферальная ссылка: {bot_link}\n"
             "Проверить рефералов можно по команде: /referrals\n"
             "Просмотреть товары: /items").format(
        count_users=count_users,
        bot_link=bot_link
    )
    if message.from_user.id == admin_id:
        text += _("\n"
                  "Добавить новый товар: /add_item")
    await bot.send_message(chat_id, text, reply_markup=languages_markup)


# Альтернативно можно использовать фильтр text_contains, он улавливает то, что указано в call.data
@dp.callback_query_handler(text_contains="lang")
async def change_language(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем последние 2 символа (например ru)
    lang = call.data[-2:]
    await db.set_language(lang)

    # После того, как мы поменяли язык, в этой функции все еще указан старый, поэтому передаем locale=lang
    await call.message.answer(_("Ваш язык был изменен", locale=lang))


@dp.message_handler(commands=["referrals"])
async def check_referrals(message: types.Message):
    referrals = await db.check_referrals()
    text = _("Ваши рефералы:\n{referrals}").format(referrals=referrals)
    await message.answer(text)


# хендлер который срабатывает при непредсказуемом запросе юзера
@dp.message_handler()
async def end(message: types.Message):
    '''Функция непредсказумогого ответа'''
    await message.answer(_('Я не знаю, что с этим делать 😲\nЯ просто напомню, что есть команда /start и /help'))
