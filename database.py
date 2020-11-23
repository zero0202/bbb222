from aiogram import types, Bot
from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, TIMESTAMP, Boolean, JSON)
from sqlalchemy import sql

from config import db_pass, db_user, host

db = Gino()


# Документация
# http://gino.fantix.pro/en/latest/tutorials/tutorial.html

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    language = Column(String(2))
    full_name = Column(String(100))
    username = Column(String(32))
    referral = Column(Integer)
    # user_age = Column(Integer)
    # user_sex = Column(String(6))
    # in_queue = Column(BigInteger, Default=False)  # Здесь хранится ID пользователей в очереди
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)


class DBCommands:

    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_new_user(self, referral=None):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name

        if referral:
            new_user.referral = int(referral)
        await new_user.create()
        return new_user

    async def set_language(self, language):
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        await user.update(language=language).apply()

    async def count_users(self) -> int:
        total = await db.func.count(User.id).gino.scalar()
        return total

    async def check_referrals(self):
        bot = Bot.get_current()
        user_id = types.User.get_current().id

        user = await User.query.where(User.user_id == user_id).gino.first()
        referrals = await User.query.where(User.referral == user.id).gino.all()

        return ", ".join([
            f"{num + 1}. " + (await bot.get_chat(referral.user_id)).get_mention(as_html=True)
            for num, referral in enumerate(referrals)
        ])

    # '''_________ГОВНО_________'''
    # # Выбор пола в начале
    # async def set_sex(self, sex):
    #     user_sex = types.User.get_current().id
    #     user = await self.get_user(user_id)
    #     await user.update(sex=sex).apply()
    # # Выбор возраста в начале
    # async def set_age(self, age):
    #     user_age = types.User.get_current().id
    #     user = await self.get_user(user_id)
    #     await user.update(age=age).apply()
    # # Поиск людей в списке in_queue
    # async def search(self, sex):

    # async def get_sex_user(self,telegram_id): """ Получить информацию о поле юзера по его айдишнику """ with
    # self.connection: result = self.cursor.execute('SELECT `sex` FROM `users` WHERE `telegram_id` = ?',(telegram_id,
    # )).fetchone() return result


async def create_db():
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/gino')

    # Create tables
    db.gino: GinoSchemaVisitor
    await db.gino.drop_all()
    await db.gino.create_all()
