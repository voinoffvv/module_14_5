import crud_functions

from random import Random
import aiogram.utils.markdown
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import markdown
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import crud_functions as crud

api = 'token'
bot = Bot(token=api)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
start_flag = False

crud.initiate_db()
all_products = crud.get_all_products()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Рассчитать калории'),
         KeyboardButton(text='🗺️ Информация')],
        [KeyboardButton(text='Купить')],
        [KeyboardButton(text='Регистрация')]
    ],
    resize_keyboard=True
)

catalog_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Продукт1', callback_data='product_buying'),
            InlineKeyboardButton(text='Продукт2', callback_data='product_buying'),
            InlineKeyboardButton(text='Продукт3', callback_data='product_buying'),
            InlineKeyboardButton(text='Продукт4', callback_data='product_buying')
        ]
    ]
)

main_menu1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
            InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
        ]
    ]
)




####################################################        RegistrationState              ###########################
class RegistrationState(StatesGroup):
    age = State()
    username = State()
    email = State()
    balance = State()

@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if crud_functions.is_included(message.text):
        await message.answer('Пользователь существует, введите другое имя:')
        await RegistrationState.username.set()
    else:
        await state.update_data(username = message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email = message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age = message.text)

    data = await state.get_data()
    crud_functions.add_user(data['username'], data['email'], data['age'])
    await state.finish()

    await message.answer('Регистрация прошла успешно!')










####################################################        UserState              ###########################
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text='Рассчитать калории')
async def main_menu(message: types.Message):
    global start_flag
    if not start_flag:
        await message.answer('Введите команду /start, чтобы начать общение.')
    else:
        await message.answer('Выберите опцию:', reply_markup=main_menu1)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.message.answer('для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст (лет):')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)

    await message.answer('Введите свой рост в см:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)

    await message.answer('Введите свой вес в кг:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)

    data = await state.get_data()
    try:
        res = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age'])
        await message.answer(f"Калории для женщин {res - 161} ккал")
        await message.answer(f"Калории для мужчин {res + 5} ккал")
    except:
        await message.answer(f"Введены некорректные данные.")
    await state.finish()


@dp.message_handler(commands='start')
async def start_message(message: types.Message):
    global start_flag
    start_flag = True
    msg = 'Привет! Я бот, помогающий твоему здоровью. Нажмите кнoпку Рассчитать.'
    await message.answer(msg, reply_markup=kb)


@dp.message_handler(text='🗺️ Информация')
async def send_information(message, state):
    await message.answer(
        'Программа производит расчет суточной нормы калорий по формуле Миффлина-Сан Жеора для мужчин и женщин.')
    await message.answer('Используйте кнопку Рассчитать')


@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    for row in all_products:
        i = 1
        try:
            await message.answer_photo(row[4], f'Название: {row[1]} | Описание: {row[2]} | Цена: {row[3]}')
            i = i + 1
        except Exception as err:
            print(err)
    await message.answer('Выберите продукт для покупки:', reply_markup=catalog_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler()
async def all_messages(message: types.Message):
    global start_flag
    if not start_flag: await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
