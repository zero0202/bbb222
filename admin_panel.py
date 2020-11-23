from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import admin_id
from load_all import dp, _, bot
from states import Mailing
from database import User


# Фича для рассылки по юзерам (учитывая их язык)
@dp.message_handler(user_id=admin_id, commands=["tell_everyone"])
async def mailing(message: types.Message):
    await message.answer(_("Пришлите текст рассылки"))
    await Mailing.Text.set()


@dp.message_handler(user_id=admin_id, state=Mailing.Text)
async def mailing(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Русский", callback_data="ru")],
            [InlineKeyboardButton(text="Узбекский", callback_data="uz")],
        ]
    )
    await message.answer(_("Пользователям на каком языке разослать это сообщение?\n\n"
                           "Текст:\n"
                           "{text}").format(text=text),
                         reply_markup=markup)
    await Mailing.Language.set()


@dp.callback_query_handler(user_id=admin_id, state=Mailing.Language)
async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")
    await state.reset_state()
    await call.message.edit_reply_markup()

    users = await User.query.where(User.language == call.data).gino.all()
    for user in users:
        try:
            await bot.send_message(chat_id=user.user_id,
                                   text=text)
            await sleep(0.3)
        except Exception:
            pass
    await call.message.answer(_("Рассылка завершена."))