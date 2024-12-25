import json
import random
from typing import List

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import keyboards.inline_keyboard
from keyboards.inline_keyboard import create_inline_kb, create_inline_kb_by_list
from database.models.models import User
from config import replics
from utils.lordfilms_reversed import lordfilm as lf
from database.redis_client import client
from config.config import FRONTEND_URL

router = Router()


class Film(StatesGroup):
    start = State()
    film = State()
    choosing_film = State()
    more_films = State()
    download = State()
    choose_quality = State()
    captcha = State()

@router.message(CommandStart())
async def start_message(message: Message, state: FSMContext):
    await state.clear()
    user, created = await User.get_or_create(telegram_id=message.from_user.id, defaults={"balance": 0.0})
    if created:
        await message.answer(
            replics.hello_no_reg,
            reply_markup=create_inline_kb(1, 'Начать')
        )
    else:
        await message.answer(
            replics.hello_reg,
            reply_markup=create_inline_kb(1, 'Начать', 'Статистика')
        )
    await state.set_state(Film.start)

@router.callback_query(F.data, Film.start)
async def start_finding(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Начать':
        await callback.message.answer('Введите название фильма')
        await state.set_state(Film.film)
    if callback.data == 'Статистика':
        pass

@router.message(F.text, Film.film)
async def film_title(message: Message, state: FSMContext):
    message_to_edit = await message.answer(f"Ищу фильм {message.text}...🎬\nПодожди немного, это может занять пару секунд!")
    founded: List[dict] = lf.searching_film(message.text)
    await state.update_data(films = founded)
    await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=message_to_edit.message_id, text=f'По твоему запросу нашлось {len(founded)} фильмов(а)', reply_markup=create_inline_kb(1, 'Посмотреть результаты'))
    await state.set_state(Film.choosing_film)


@router.callback_query(F.data == 'Посмотреть результаты', Film.choosing_film)
async def choosing_film(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(page=0)

    film = data['films'][0]
    keyboard = create_inline_kb(1, 'Еще ->', 'Смотреть')

    await callback_query.message.bot.delete_message(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id)
    await callback_query.message.bot.send_photo(
        chat_id=callback_query.from_user.id,
        caption=film['title'],
        photo=film['img'],
        reply_markup=keyboard
    )

    await state.set_state(Film.more_films)


@router.callback_query(F.data == 'Еще ->', Film.more_films)
async def more_films(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get('page', 0)
    page += 1
    await state.update_data(page=page)

    if page < len(data['films']):
        film = data['films'][page]
        keyboard = create_inline_kb(1, 'Еще ->', 'Смотреть')

        await callback_query.message.bot.delete_message(chat_id=callback_query.from_user.id,
                                                        message_id=callback_query.message.message_id)
        await callback_query.message.bot.send_photo(
            chat_id=callback_query.from_user.id,
            caption=film['title'],
            photo=film['img'],
            reply_markup=keyboard
        )
    else:
        await callback_query.message.answer("Больше фильмов нет.\nПопробуй еще раз, если нашлось твоего фильма - /start.")

@router.callback_query(F.data == 'Смотреть', Film.more_films)
async def download_film(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Film.download)
    await state.update_data(title_film = callback_query.message.caption)
    data = await state.get_data()
    film_url = [i for i in data['films'] if i['title'] == callback_query.message.caption]
    await state.update_data(image = film_url[0]['img'])
    await callback_query.message.bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    if film_url:
        try:
            host_links = lf.get_links_on_host(film_url[0]['url'])
            qualities = lf.get_qualities(host_links)
            keys = list(qualities.keys())
            if 'fullHd' in keys and 'highUrl' in keys and 'mediumUrl' in keys and 'lowUrl' in keys:
                await callback_query.message.answer('Выберите качество, в котором хотите скачать или посмотреть фильм.',
                                                    reply_markup=create_inline_kb(1, 'FullHD (Максимальное)', 'HD', '480p', '360p'))
            elif 'fullHd' not in keys and 'highUrl' in keys and 'mediumUrl' in keys and 'lowUrl' in keys:
                await callback_query.message.answer('Выберите качество, в котором хотите скачать или посмотреть фильм.',
                                                    reply_markup=create_inline_kb(1,  'HD', '480p', '360p'))
            elif 'fullHd' not in keys and 'highUrl' not in keys and 'mediumUrl' in keys and 'lowUrl' in keys:
                await callback_query.message.answer('Выберите качество, в котором хотите скачать или посмотреть фильм.',
                                                    reply_markup=create_inline_kb(1, '480p', '360p'))
            elif 'fullHd' not in keys and 'highUrl' not in keys and 'mediumUrl' not in keys and 'lowUrl' in keys:
                await callback_query.message.answer('Выберите качество, в котором хотите скачать или посмотреть фильм.',
                                                    reply_markup=create_inline_kb(1, '360p'))
            await state.update_data(download_links = qualities)
            await state.set_state(Film.choose_quality)
        except Exception as e:
            await callback_query.message.answer('К сожалению, такого фильма пока нет в моей базе :(, прости за неудобства.')

@router.callback_query(F.data.in_(['FullHD (Максимальное)', 'HD', '480p', '360p']), Film.choose_quality)
async def choose_quality(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    quality_to_url = {
        'FullHD (Максимальное)': data['download_links']['fullHd'],
        'HD': data['download_links']['highUrl'],
        '480p': data['download_links']['mediumUrl'],
        '360p': data['download_links']['lowUrl']
    }
    selected_url = quality_to_url.get(callback.data)
    if not selected_url:
        await callback.message.answer("Некорректное качество. Попробуйте ещё раз.")
        return

    base_url = f"{FRONTEND_URL}/watch?id={callback.from_user.id}"
    await client.setex(name=callback.from_user.id, value=json.dumps({'url': selected_url, "title": data["title_film"], 'image': data['image']}), time=10_800)
    await state.update_data(base_url = base_url)
    first = random.randint(0, 15)
    operation = random.choice(['+', '*'])
    second = random.randint(0, 15)
    true_answer = first + second if operation == '+' else first * second
    await state.update_data(true_answer = str(true_answer))
    buttons = [str(random.randint(0, 5)), str(random.randint(6, 10)), str(random.randint(11, 15)), str(true_answer)]
    random.shuffle(buttons)
    await callback.message.answer(f'Для начала просмотра пройдите проверку, что вы не робот. Решите простой пример.\n\nСколько будет <b>{first}{operation}{second}</b>?',
                                  reply_markup=create_inline_kb_by_list(1, buttons))
    await state.set_state(Film.captcha)


@router.callback_query(F.data.in_([str(i) for i in range(0, 300)]), Film.captcha)
async def go_watching(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == data['true_answer']:
        await callback.message.bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await callback.message.answer(
            '⬇️По кнопке ниже ты сможешь посмотреть фильм онлайн, либо скачать его.⬇️\n\nПриятного просмотра! ️',
            reply_markup=keyboards.inline_keyboard.create_url_kb(1, 'Начать просмотр', data['base_url']))
