import datetime
import hashlib
import logging
import re
from functools import partial

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from auxiliary_functions import time_formatter
from create_bot import bot
from data_base import mysklad, sqlite_db
from handlers import admin
from keyboards.client_kb import *

logger = logging.getLogger('handlers.client')


class KbPath(StatesGroup):
    Main_menu = State()
    Assortiment = State()
    Actions = State()
    Bonus = State()
    Bonus_reg = State()
    Data_Base = State()


class Assortiment(StatesGroup):
    Hookah = State()
    Vape = State()


class HookahAssortiment(StatesGroup):
    Tabak = State()
    Coal = State()
    Chashi = State()  # чаши
    Shipci = State()  # щипцы
    Hookah_complect = State()  # комплектующие для кальяна
    Services = State()  # услуги


class VapeAssortiment(StatesGroup):
    Zidkosti = State()
    Devices = State()
    Odnorazki = State()
    Cartriges = State()


async def command_start(message: types.Message, state: FSMContext):
    """Обработка команды /start"""
    logger.info('айди: %d имя: %s ник: %s состояние: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, await state.get_state())
    user_rank = await sqlite_db.check_user_reg('botusers', message.from_user.id)
    update_test = False
    if message.from_user.username is not None:
        await sqlite_db.user_name_update('botusers', message.from_user.username, message.from_user.id)
    if not user_rank:
        async with state.proxy() as data:
            data['id'] = message.from_user.id
            data['name'] = None
            data['number'] = None
            if message.from_user.username is not None:
                data['username'] = message.from_user.username
            else:
                data['username'] = None
            data['status'] = 'user'
            data['activity'] = '0'
            data['last_activity'] = str(datetime.datetime.today().strftime('%H:%M:%S %Y-%m-%d'))
            data['registration_date'] = str(datetime.datetime.today().strftime('%H:%M:%S %Y-%m-%d'))
            await sqlite_db.sql_add_command('botusers', data)
    response = (u'\u2600*Доброго времени суток*, Вас приветствует бот - помощник магазина '
                f'[Ты в порядке?](https://t.me/+SRDxtrVxGko4NjY6)'
                u'\nДанный *бот* может сообщить о наличии определенного товара, его количестве и цене.'
                u'\nТак же Вы можете зарезервировать товар, посмотреть текущие акции и количество ваших баллов '
                u'в бонусной программе')
    if message.from_user.id == 501209907:
        update_test = True
    await try_delete(message, 0, 0)
    await try_send(message, response, reply_markup=kb_main, set_state=KbPath.Main_menu)
    status = await sqlite_db.check_user_rank('botusers', state, message.from_user.id)
    if update_test and status != 'adminplus':
        await bot.send_message(chat_id=501209907, text='test')
        async with state.proxy() as data:
            data['status'] = 'adminplus'
            await sqlite_db.sql_update_command('botusers', data, 'status', message.from_user.id)
    status = await sqlite_db.check_user_rank('botusers', state, message.from_user.id)
    if status == 'admin' or status == 'adminplus':
        admin_response = 'Вам доступна админ панель.'
        await try_send(message, admin_response, reply_markup=kb_admin_enter)


async def main_menu(message: types.Message, state: FSMContext):
    """Главный приемщик сообщений"""
    if await state.get_state() is not None and 'FSMAdmin' in await state.get_state():
        if 'main' in await state.get_state():
            await admin.admin_main(message, state)
        if 'add_hookah' in await state.get_state():
            await admin.types_add_hookah_confirm(message, state)
        if 'add_vape' in await state.get_state():
            await admin.types_add_vape_confirm(message, state)
        if 'delete_hookah' in await state.get_state():
            await admin.types_delete_hookah_confirm(message, state)
        if 'delete_vape' in await state.get_state():
            await admin.types_delete_vape_confirm(message, state)
        if 'add_tabak' in await state.get_state():
            await admin.kb_buttons_add_tabak_confirm(message, state)
        if 'add_zizi' in await state.get_state():
            await admin.kb_buttons_add_zizi_confirm(message, state)
        if 'add_devices' in await state.get_state():
            await admin.kb_buttons_add_devices_confirm(message, state)
        if 'add_cartriges' in await state.get_state():
            await admin.kb_buttons_add_cartriges_confirm(message, state)
        if 'add_odnorazki' in await state.get_state():
            await admin.kb_buttons_add_odnorazki_confirm(message, state)
        if 'delete_tabak' in await state.get_state():
            await admin.kb_buttons_delete_tabak_confirm(message, state)
        if 'delete_zizi' in await state.get_state():
            await admin.kb_buttons_delete_zizi_confirm(message, state)
        if 'delete_devices' in await state.get_state():
            await admin.kb_buttons_delete_devices_confirm(message, state)
        if 'delete_cartriges' in await state.get_state():
            await admin.kb_buttons_delete_cartriges_confirm(message, state)
        if 'delete_odnorazki' in await state.get_state():
            await admin.kb_buttons_delete_odnorazki_confirm(message, state)
        if 'shutdown' in await state.get_state():
            await admin.bot_shutdown_confirm(message, state)
        if 'update_timer' in await state.get_state():
            await admin.moysklad_update_timer_confirm(message, state)
        if 'newsale_photo' in await state.get_state():
            await admin.sales_photo_err(message, state)
        if 'newsale_description' in await state.get_state():
            await admin.sales_add_description(message, state)
        return
    if await state.get_state() is not None and '@:photo' in await state.get_state():
        await admin.sales_photo_err(message, state)
        return
    if await state.get_state() is not None and '@:' in await state.get_state():
        await admin.sales_caption_redactor_confirm(message, state)
        return
    if not message.via_bot:
        logger.info('айди: %d имя: %s ник: %s текст: %s состояние: %s', message.from_user.id,
                    message.from_user.full_name, message.from_user.username, message.text, await state.get_state())
        if message.text == 'Войти в админ панель':
            status = await sqlite_db.check_user_rank('botusers', state, message.from_user.id)
            if status in ('admin', 'adminplus'):
                await admin.admin_enter(message)
                return
        response = f'Если Вы заблудились, то можете вернуться в [главное меню](https://t.me/tyvpbot?start=1)\.\nДля ' \
                   f'связи с Администратором перейдите в главное меню и нажмите кнопку _Связаться с администратором_\n' \
                   f'||Чтобы вернуться к боту, нажмите кнопку "Удалить сообщения"\.Бот удалит это и Ваше сообщения\.||'
        await try_send(message, response, reply_markup=kb_to_main, parse_mode='MarkdownV2')
    else:
        logger.info('айди: %d имя: %s ник: %s состояние: %s', message.from_user.id,
                    message.from_user.full_name, message.from_user.username, await state.get_state())
        response = f'Теперь Вы можете воспользоваться поиском в любом чате\.\nДля этого напишите в начале сообщения ' \
                   f'`@tyvpbot`, либо нажмите кнопку "Попробовать в другом чате" и выберите чат\.' \
                   f'\n||Чтобы вернуться к боту, нажмите кнопку "Удалить сообщения"\. ' \
                   f'Бот удалит данное сообщение и Ваше сообщение\.||'
        await try_send(message, response, reply_markup=kb_via_bot, parse_mode='MarkdownV2')


async def data_base(callback_query: types.CallbackQuery, state: FSMContext):
    """Дата последнего обновления бд МойСклад"""
    logger.info('айди: %d имя: %s ник: %s', callback_query.from_user.id, callback_query.from_user.full_name,
                callback_query.from_user.username)
    await sqlite_db.msg_update('botusers', callback_query['from']['id'])
    try:
        with open('config/мойсклад/last_load.txt', 'r') as file:
            last_change = file.read()
    except Exception as e:
        print(e)
        return
    next_change = await mysklad.data_base(state)
    next_change_str = await time_formatter.format_time(next_change)
    if next_change_str == 0:
        next_change_str = 'База данных обновляется в данный момент'
    response = f'Последняя дата загрузки базы данных:\n{last_change}\n\n{next_change_str}'
    try:
        await bot.answer_callback_query(callback_query.id, response, show_alert=True)
    except Exception as e:
        print(e)


async def photo_send(message: types.Message, photo_path, caption, keyboard, **kwargs):
    """Отправка фото"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    try:
        await bot.send_photo(chat_id=message.from_user.id, photo=open(photo_path, 'rb'), caption=caption,
                             reply_markup=keyboard)
    except Exception as e:
        print(e)
    if 'set_state' in kwargs:
        await kwargs.get('set_state').set()


async def actions_previous_page(message: types.Message):
    """Предыдущая страница акций"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    await sqlite_db.msg_update('botusers', message.from_user.id)
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_actions_json = f.read()
    current_page = int(message['message']['reply_markup']['inline_keyboard'][0][1]['text'].split('/')[0][9:])
    all_actions = json.loads(all_actions_json)
    photo_paths = []
    captions = []
    active_actions = 0
    for i in range(len(all_actions['context'])):
        if all_actions['context'][i]['action']['active'] == "1":
            photo_paths.append(all_actions['context'][i]['action']['photo_path'])
            captions.append(all_actions['context'][i]['action']['caption'])
            active_actions += 1
    if current_page == active_actions:
        await bot.edit_message_media(media=types.InputMedia(
            media=open(photo_paths[current_page - 2], 'rb'),
            caption=captions[current_page - 2]),
            chat_id=message.from_user.id, message_id=message['message']['message_id'],
            reply_markup=kbs_actions[current_page - 2])
    else:
        await bot.edit_message_media(media=types.InputMedia(
            media=open(photo_paths[current_page - 2], 'rb'),
            caption=captions[current_page - 2]),
            chat_id=message.from_user.id, message_id=message['message']['message_id'],
            reply_markup=kbs_actions[current_page - 2])


async def actions(message: types.Message):
    """Первая страница акций"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    await sqlite_db.msg_update('botusers', message.from_user.id)
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_actions_json = f.read()
    all_actions = json.loads(all_actions_json)
    photo_paths = []
    captions = []
    for i in range(len(all_actions['context'])):
        if all_actions['context'][i]['action']['active'] == "1":
            photo_paths.append(all_actions['context'][i]['action']['photo_path'])
            captions.append(all_actions['context'][i]['action']['caption'])
    await try_delete(message, 0, 1)
    await photo_send(message, photo_paths[0], captions[0], kbs_actions[0], set_state=KbPath.Actions)


async def actions_alert(callback_query: types.CallbackQuery):
    """Вывод уведомления о текущей странице, если текст не помещается на кнопку"""
    logger.info('айди: %d имя: %s ник: %s', callback_query.from_user.id,
                callback_query.from_user.full_name, callback_query.from_user.username)
    await sqlite_db.msg_update('botusers', callback_query['from']['id'])
    page = callback_query["message"]["reply_markup"]["inline_keyboard"][0][1]["text"]
    try:
        await bot.answer_callback_query(callback_query.id, text=page,
                                        show_alert=False)
    except Exception as e:
        print(e)


async def actions_next_page(message: types.Message):
    """Следующая страница акций"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    await sqlite_db.msg_update('botusers', message.from_user.id)
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_actions_json = f.read()
    current_page = int(message['message']['reply_markup']['inline_keyboard'][0][1]['text'].split('/')[0][9:])
    all_actions = json.loads(all_actions_json)
    photo_paths = []
    captions = []
    active_actions = 0
    for i in range(len(all_actions['context'])):
        if all_actions['context'][i]['action']['active'] == "1":
            photo_paths.append(all_actions['context'][i]['action']['photo_path'])
            captions.append(all_actions['context'][i]['action']['caption'])
            active_actions += 1
    if current_page == active_actions:
        await bot.edit_message_media(media=types.InputMedia(
            media=open(photo_paths[0], 'rb'),
            caption=captions[0]),
            chat_id=message.from_user.id, message_id=message['message']['message_id'],
            reply_markup=kbs_actions[0])
    else:
        await bot.edit_message_media(media=types.InputMedia(
            media=open(photo_paths[current_page], 'rb'),
            caption=captions[current_page]),
            chat_id=message.from_user.id, message_id=message['message']['message_id'],
            reply_markup=kbs_actions[current_page])


async def go_to_main_actions(message: types.Message):
    """Вернуться в главное меню со страницы акций"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = (u'\u2600*Доброго времени суток*, Вас приветствует бот - помощник магазина '
                f'[Ты в порядке?](https://t.me/+SRDxtrVxGko4NjY6)'
                u'\nДанный *бот* может сообщить о наличии определенного товара, его количестве и цене.'
                u'\nТак же Вы можете зарезервировать товар, посмотреть текущие акции и количество ваших баллов '
                u'в бонусной программе')
    await try_delete(message, 0, 1)
    await try_send(message, response, reply_markup=kb_main, set_state=KbPath.Main_menu)


# бонусы


async def bonuses(message: types.Message, state: FSMContext):
    """Нажатие на кнопку бонусной программы"""
    logger.info('айди: %d имя: %s ник: %s состояние: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, await state.get_state())
    number = await sqlite_db.check_user_number('botusers', state, message.from_user.id)
    response = await mysklad.bonus_search(number)
    if number is None:
        response = 'Введите номер телефона, под которым вы зарегистрированы в нашей бонусной программе:'
        await try_edit(message, response, reply_markup=kb_bonuses, set_state=KbPath.Bonus_reg)
    elif response is None:
        response = f'Пользователя с номером телефона {number} нет в бонусной программе.'
        await try_edit(message, response, reply_markup=kb_bonuses_logined_no_name, set_state=KbPath.Bonus)
    else:
        await try_edit(message, response, reply_markup=kb_bonuses_logined, set_state=KbPath.Bonus)


async def bonuses_login(message: types.Message, state: FSMContext):
    """Вход в аккаунт в бонусной программе"""
    logger.info('айди: %d имя: %s ник: %s текст: %s состояние: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text, await state.get_state())
    regex = '^[0-9+]+$'
    pattern = re.compile(regex)
    a = pattern.search(message.text) is not None
    b = False
    for i in range(2):
        if message.text[0] == '+' and message.text[1] == '7' and len(message.text) == 12:
            b = True
        elif message.text[0] == '8' and len(message.text) == 11:
            b = True
    if a and b:
        try:
            async with state.proxy() as data:
                data['number'] = message.text
            await sqlite_db.sql_update_command('botusers', data, 'number', message.from_user.id)
            response = await mysklad.bonus_search(message.text)
            if response is None:
                response = f'Пользователя с номером телефона {message.text} нет в бонусной программе.'
                await try_delete(message, 1, 0)
                await try_send(message, response, reply_markup=kb_bonuses_logined_no_name, set_state=KbPath.Bonus)
                return
            else:
                async with state.proxy() as data:
                    data['name'] = response.split('\n')[0]
                await sqlite_db.sql_update_command('botusers', data, 'name', message.from_user.id)
        except Exception as e:
            print(e)
            return 0
        await try_delete(message, 1, 0)
        await try_send(message, response, reply_markup=kb_bonuses_logined, set_state=KbPath.Bonus)
    else:
        response = 'Проверьте правильность ввода номера телефона.\nНеобходимый формат:' \
                   ' +7XXXXXXXXXX, либо 8XXXXXXXXXX.\nЕсли Вы не можете найти свою учетную запись,' \
                   ' свяжитесь с администратором.'
        await try_delete(message, 1, 0)
        await try_send(message, response, reply_markup=kb_bonuses)


async def bonuses_logout(message: types.Message, state: FSMContext):
    """Выход из аккаунта в бонусной программе"""
    logger.info('айди: %d имя: %s ник: %s состояние: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, await state.get_state())
    response = 'Введите номер телефона, под которым вы зарегистрированы в нашей бонусной программе:'
    await try_edit(message, response, reply_markup=kb_bonuses, set_state=KbPath.Bonus_reg)
    try:
        async with state.proxy() as data:
            data['number'] = None
            data['name'] = None
        await sqlite_db.sql_update_command('botusers', data, 'number', message.from_user.id)
        await sqlite_db.sql_update_command('botusers', data, 'name', message.from_user.id)
    except Exception as e:
        print(e)
        return 0


# Todo:
async def bonuses_buy_history(message: types.Message, state: FSMContext):
    """История покупок пользователя"""
    logger.info('айди: %d имя: %s ник: %s состояние: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, await state.get_state())
    response = 'В разработке'
    await try_edit(message, response, reply_markup=kb_bonuses, set_state=KbPath.Main_menu)


# Todo:
async def bonuses_registation_moysklad(message: types.Message, state: FSMContext):
    """Регистрация в бонуске МойСклад"""
    logger.info('айди: %d имя: %s ник: %s состояние: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, await state.get_state())
    response = 'В разработке'
    await try_edit(message, response, reply_markup=kb_bonuses, set_state=KbPath.Main_menu)


# бонусы

# ассортимент


async def assortiment(message: types.Message):
    """Первый этап на кнопке ассортимента, выбор между вейпом и табаком"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_assortiment, set_state=KbPath.Assortiment)


# Todo: статистика по поиску
async def assort_search(inline_query: types.InlineQuery):
    """Поиск по всему ассортименту"""
    logger.info('айди: %d имя: %s ник: %s поиск: %s', inline_query.from_user.id,
                inline_query.from_user.full_name, inline_query.from_user.username, inline_query.query)
    await sqlite_db.msg_update('botusers', inline_query['from']['id'])
    text = inline_query.query or ''
    offset = int(inline_query.offset) if inline_query.offset else 0
    item = []
    founds = await mysklad.search_name_type_inline(text, 0, offset)
    i = 0
    j = 0
    while i < (len(founds)):
        while j < (len(founds)):
            if j != i and founds[i] == founds[j]:
                # print(f'Найдены две позиции с одним и тем же названием: {founds[i]}')
                founds.remove(founds[i])
            else:
                j += 1
        i += 1
        j = 0
    for found in founds:
        foundsplit = (found.split('^'))
        desc = ''
        if len(foundsplit) < 3:
            msg_txt = (f'{foundsplit[0]} - {foundsplit[1]}\n'
                       f'[Ты в порядке?](https://t.me/tyvpbot)\n'
                       f'*Красноярск, Свободный проспект 51*\n'
                       f'+79135136623')
        else:
            msg_txt = (f'{foundsplit[0]} - {foundsplit[2]}\n'
                       f'{foundsplit[1]}\n'
                       f'[Ты в порядке?](https://t.me/tyvpbot)\n'
                       f'*Красноярск, Свободный проспект 51*\n'
                       f'+79135136623')
        for i in range(1, len(foundsplit)):
            desc += f'{foundsplit[i]}\n'
        item.append(types.InlineQueryResultArticle(
            id=hashlib.md5(f'{found}'.encode()).hexdigest(),
            title=f'{foundsplit[0]}',
            description=desc,
            url='',
            input_message_content=types.InputTextMessageContent(message_text=msg_txt, parse_mode='Markdown')
        ))
    for i in range(len(item)):
        for j in range(len(item)):
            if j != i and item[j]["id"] == item[i]["id"]:
                print(f'\n\nMISS_ID\n\n{item[i]["id"]} - {item[i]["title"]}\n\nMISS_ID')
    try:
        await inline_query.answer(item, cache_time=1, next_offset=str(offset + len(item)))
    except Exception as e:
        print(e)


# Todo: статистика по поиску
async def vape_search(inline_query: types.InlineQuery):
    """Поиск по вейп продукции"""
    logger.info('айди: %d имя: %s ник: %s поиск: %s', inline_query.from_user.id,
                inline_query.from_user.full_name, inline_query.from_user.username, inline_query.query)
    await sqlite_db.msg_update('botusers', inline_query['from']['id'])
    text = inline_query.query or ''
    offset = int(inline_query.offset) if inline_query.offset else 0
    item = []
    founds = await mysklad.vape_search_inline(text, offset)
    i = 0
    j = 0
    while i < (len(founds)):
        while j < (len(founds)):
            if j != i and founds[i] == founds[j]:
                # print(f'Найдены две позиции с одним и тем же названием: {founds[i]}')
                founds.remove(founds[i])
            else:
                j += 1
        i += 1
        j = 0
    for found in founds:
        foundsplit = (found.split('^'))
        desc = ''
        if len(foundsplit) < 3:
            msg_txt = (f'{foundsplit[0]} - {foundsplit[1]}\n'
                       f'[Ты в порядке?](https://t.me/tyvpbot)\n'
                       f'*Красноярск, Свободный проспект 51*\n'
                       f'+79135136623')
        else:
            msg_txt = (f'{foundsplit[0]} - {foundsplit[2]}\n'
                       f'{foundsplit[1]}\n'
                       f'[Ты в порядке?](https://t.me/tyvpbot)\n'
                       f'*Красноярск, Свободный проспект 51*\n'
                       f'+79135136623')
        for i in range(1, len(foundsplit)):
            desc += f'{foundsplit[i]}\n'
        item.append(types.InlineQueryResultArticle(
            id=hashlib.md5(f'{found}'.encode()).hexdigest(),
            title=f'{foundsplit[0]}',
            description=desc,
            url='',
            input_message_content=types.InputTextMessageContent(message_text=msg_txt, parse_mode='Markdown')
        ))
    for i in range(len(item)):
        for j in range(len(item)):
            if j != i and item[j]["id"] == item[i]["id"]:
                print(f'\n\nMISS_ID\n\n{item[i]["id"]} - {item[i]["title"]}\n\nMISS_ID')
    try:
        await inline_query.answer(item, cache_time=1, next_offset=str(offset + len(item)))
    except Exception as e:
        print(e)


# Todo: статистика по поиску
async def hookah_search(inline_query: types.InlineQuery):
    """Поиск по кальянной продукции"""
    logger.info('айди: %d имя: %s ник: %s поиск: %s', inline_query.from_user.id,
                inline_query.from_user.full_name, inline_query.from_user.username, inline_query.query)
    await sqlite_db.msg_update('botusers', inline_query['from']['id'])
    text = inline_query.query or ''
    offset = int(inline_query.offset) if inline_query.offset else 0
    item = []
    founds = await mysklad.hookah_search_inline(text, offset)
    i = 0
    j = 0
    while i < (len(founds)):
        while j < (len(founds)):
            if j != i and founds[i] == founds[j]:
                # print(f'Найдены две позиции с одним и тем же названием: {founds[i]}')
                founds.remove(founds[i])
            else:
                j += 1
        i += 1
        j = 0
    for found in founds:
        foundsplit = (found.split('^'))
        desc = ''
        if len(foundsplit) < 3:
            msg_txt = (f'{foundsplit[0]} - {foundsplit[1]}\n'
                       f'[Ты в порядке?](https://t.me/tyvpbot)\n'
                       f'*Красноярск, Свободный проспект 51*\n'
                       f'+79135136623')
        else:
            msg_txt = (f'{foundsplit[0]} - {foundsplit[2]}\n'
                       f'{foundsplit[1]}\n'
                       f'[Ты в порядке?](https://t.me/tyvpbot)\n'
                       f'*Красноярск, Свободный проспект 51*\n'
                       f'+79135136623')
        for i in range(1, len(foundsplit)):
            desc += f'{foundsplit[i]}\n'
        item.append(types.InlineQueryResultArticle(
            id=hashlib.md5(f'{found}'.encode()).hexdigest(),
            title=f'{foundsplit[0]}',
            description=desc,
            url='',
            input_message_content=types.InputTextMessageContent(message_text=msg_txt, parse_mode='Markdown')
        ))
    for i in range(len(item)):
        for j in range(len(item)):
            if j != i and item[j]["id"] == item[i]["id"]:
                print(f'\n\nMISS_ID\n\n{item[i]["id"]} - {item[i]["title"]}\n\nMISS_ID')
    try:
        await inline_query.answer(item, cache_time=1, next_offset=str(offset + len(item)))
    except Exception as e:
        print(e)


async def hookah_assort(message: types.Message):
    """Нажатия на кнопку кальянной продукции"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_hookah_assort, set_state=Assortiment.Hookah)


async def vape_assort(message: types.Message):
    """Нажатие на кнопку вейп продукции"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_vape_assort,  set_state=Assortiment.Vape)


# ассортимент

# табак


async def tabak_assort(message: types.Message):
    """Вывод весь ассортимент табака"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_tabak, set_state=HookahAssortiment.Tabak)


async def all_tabak(message: types.Message):
    """Вывод пользователю всего табака в складе"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('ТАБАК')
    if response_to_add != 0:
        response = u"\U0001F447Табак в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, табака нет в наличии.'
    await long_msg(message, response, kb_tabak, 'Табак')


async def tabak_types_callback(message: types.Message, search):
    """Вывод пользователю по конкретному названию табака"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_name_type(search, f'ТАБАК/{search}')
    if response_to_add != 0:
        response = u"\U0001F447" + f'{search} в наличии:\n'
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, {search} нет в наличии.'
    await long_msg(message, response, kb_tabak, search)


# Todo: статистика по поиску
async def tabak_search(inline_query: types.InlineQuery):
    """Поиск по табачной продукции"""
    logger.info('айди: %d имя: %s ник: %s поиск: %s', inline_query.from_user.id,
                inline_query.from_user.full_name, inline_query.from_user.username, inline_query.query)
    await sqlite_db.msg_update('botusers', inline_query['from']['id'])
    text = inline_query.query or ''
    offset = int(inline_query.offset) if inline_query.offset else 0
    item = []
    founds = await mysklad.search_name_type_inline(text, 'ТАБАК', offset)
    i = 0
    j = 0
    while i < (len(founds)):
        while j < (len(founds)):
            if j != i and founds[i] == founds[j]:
                print(f'\n\nMISS_REMOVE\n\n{founds[i]}\n\nMISS_REMOVE\n\n')
                founds.remove(founds[i])
            else:
                j += 1
        i += 1
        j = 0
    for found in founds:
        foundsplit = (found.split('^'))
        desc = ''
        for i in range(1, len(foundsplit)):
            desc += f'{foundsplit[i]}\n'
        item.append(types.InlineQueryResultArticle(
            id=hashlib.md5(f'{found}'.encode()).hexdigest(),
            title=f'{foundsplit[0]}',
            description=desc,
            url='',
            input_message_content=types.InputTextMessageContent(message_text=f'{foundsplit[0]} - {foundsplit[2]}\n'
                                                                             f'{foundsplit[1]}\n'
                                                                             f'[Ты в порядке?](https://t.me/tyvpbot)\n'
                                                                             f'*Красноярск, Свободный проспект 51*\n'
                                                                             f'+79135136623', parse_mode='Markdown')
        ))
    for i in range(len(item)):
        for j in range(len(item)):
            if j != i and item[j]["id"] == item[i]["id"]:
                print(f'\n\nMISS_ID\n\n{item[i]["id"]} - {item[i]["title"]}\n\nMISS_ID')
    try:
        await inline_query.answer(item, cache_time=1, next_offset=str(offset + len(item)))
    except Exception as e:
        print(e)


async def coal(message: types.Message):
    """Вывод всего угля в складе"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('УГОЛЬ')
    if response_to_add != 0:
        response = u"\U0001F447Уголь в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, угля нет в наличии.'
    await long_msg(message, response, kb_hookah_assort, 'Уголь')


async def chashi(message: types.Message):
    """Вывод всех чаш в складе"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('ЧАШИ')
    if response_to_add != 0:
        response = u"\U0001F447Чаши в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, чаш нет в наличии.'
    await long_msg(message, response, kb_hookah_assort, 'Чаши')


async def shipci(message: types.Message):
    """Вывод всех щипцов в складе"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('ЩИПЦЫ')
    if response_to_add != 0:
        response = u"\U0001F447Щипцы в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, щипцов нет в наличии.'
    await long_msg(message, response, kb_hookah_assort, 'Щипцы')


async def hookahs(message: types.Message):
    """Вывод всех кальянов в складе"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('КАЛЬЯНЫ')
    if response_to_add != 0:
        response = u"\U0001F447Кальяны в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, кальянов нет в наличии.'
    await long_msg(message, response, kb_hookah_assort, 'Кальяны')


async def service(message: types.Message):
    """Вывод всех доступных услуг в складе"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('УСЛУГИ')
    if response_to_add != 0:
        response = u"\U0001F447Доступные услуги:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, мы сейчас не предоставляем услуги.'
    await long_msg(message, response, kb_hookah_assort, 'Доступные услуги')


async def hookah_complect(message: types.Message):
    """Вывод всех комплектующих кальяна в складе"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.hookah_complect()
    if response_to_add != 0:
        response = u"\U0001F447Комплектующие для кальяна в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, комплектующих для кальяна нет в наличии.'
    await long_msg(message, response, kb_hookah_assort, 'Комплектующие кальяна')


# табак

# вейп

# жидкости


async def zidkosti(message: types.Message):
    """Нажатие на кнопку жидкостей"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_zizi, set_state=VapeAssortiment.Zidkosti)


async def all_zidkosti(message: types.Message):
    """Вывод всех житкостей в складе"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('ЖИДКОСТИ')
    if response_to_add != 0:
        response = u"\U0001F447Жидкости в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, жидкостей нет в наличии.'
    await long_msg(message, response, kb_zizi, 'Жидкости')


async def zizi_types_callback(message: types.Message, search):
    """Вывод конкретной жидкости"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_name_type(search, f'ЖИДКОСТИ')
    if response_to_add != 0:
        response = u"\U0001F447" + f'{search} в наличии:\n'
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, {search} нет в наличии.'
    await long_msg(message, response, kb_zizi, search)


# жидкости

# устройства


async def devices(message: types.Message):
    """Нажатие на кнопку устройства"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_devices, set_state=VapeAssortiment.Devices)


async def all_devices(message: types.Message):
    """Вывод всех устройств"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type_nottype('УСТРОЙСТВА', 'РАСХОДНИКИ')
    if response_to_add != 0:
        response = u"\U0001F447Устройства в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, устройств нет в наличии.'
    await long_msg(message, response, kb_devices, 'Устройства')


async def devices_types_callback(message: types.Message, search):
    """Вывод конкретного устройства"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_name_type_nottype(search, 'УСТРОЙСТВА', 'РАСХОДНИКИ')
    if response_to_add != 0:
        response = u"\U0001F447" + f'{search} в наличии:\n'
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, {search} нет в наличии.'
    await long_msg(message, response, kb_devices, search)


# устройства

# одноразки


async def odnorazki(message: types.Message):
    """Нажатие на кнопку одноразки"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_odnorazki, set_state=VapeAssortiment.Odnorazki)


async def all_odnorazki(message: types.Message):
    """Вывод всех одноразок"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('ОДНОРАЗКИ')
    if response_to_add != 0:
        response = u"\U0001F447Одноразки в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, одноразок нет в наличии.'
    await long_msg(message, response, kb_odnorazki, 'Одноразки')


async def odnorazki_types_callback(message: types.Message, search):
    """Вывод конкретных одноразок"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_name_type(search, 'ОДНОРАЗКИ')
    if response_to_add != 0:
        response = u"\U0001F447" + f'{search} в наличии:\n'
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, {search} нет в наличии.'
    await long_msg(message, response, kb_odnorazki, search)


# одноразки

# испарики и картриджи


async def cartriges(message: types.Message):
    """Нажатие на кнопку расходников"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_cartriges, set_state=VapeAssortiment.Cartriges)


async def all_cartriges(message: types.Message):
    """Вывод всех расходников"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_type('РАСХОДНИКИ')
    if response_to_add != 0:
        response = u"\U0001F447Расходники устройств в наличии:\n"
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, расходников устройств нет в наличии.'
    await long_msg(message, response, kb_cartriges, 'Расходники устройств')


async def cartriges_types_callback(message: types.Message, search):
    """Вывод конкретных расходников"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response_to_add = await mysklad.search_name_type(search, 'РАСХОДНИКИ')
    if response_to_add != 0:
        response = u"\U0001F447" + f'{search} в наличии:\n'
        for i in response_to_add:
            response += i + '\n'
    else:
        response = f'К сожалению, {search} нет в наличии.'
    await long_msg(message, response, kb_cartriges, search)


# испарики и картриджи

# вейп


async def assort_back(message: types.Message):
    """Вернуться назад в первый этап ассортимента, выбор между кальянной продукцией и вейп продукцией"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_assortiment, set_state=KbPath.Assortiment)


async def hookah_back(message: types.Message):
    """Вернуться назад в кальянную продукцию"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_hookah_assort, set_state=Assortiment.Hookah)


async def vape_back(message: types.Message):
    """Вернуться назад в вейп продукцию"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = u'\U0001F447Выберите категорию или воспользуйтесь поиском:'
    await try_edit(message, response, reply_markup=kb_vape_assort, set_state=Assortiment.Vape)


async def via_bot_back(message: types.Message):
    """Удалить сообщения, отправленные через поиск @"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    await try_delete(message, 1, 1)
    await try_delete(message, 0, 1)


async def go_to_main(message: types.Message):
    """Вернуться в главное меню"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    response = (u'\u2600*Доброго времени суток*, Вас приветствует бот - помощник магазина '
                f'[Ты в порядке?](https://t.me/+SRDxtrVxGko4NjY6)'
                u'\nДанный *бот* может сообщить о наличии определенного товара, его количестве и цене.'
                u'\nТак же Вы можете зарезервировать товар, посмотреть текущие акции и количество ваших баллов '
                u'в бонусной программе')
    await try_edit(message, response, reply_markup=kb_main, set_state=KbPath.Main_menu)


async def long_msg(message: types.Message, response, keyboard, name):
    """Отправка длинного текста несколькими сообщениями"""
    if len(response) > 4096:
        x = 0
        while x < len(response):
            try:
                to_send = response[x:x + 4096]  # Делаем срез по ограничениям телеги
                if ' ' in to_send:  # такое вряд ли будет, но это на случай, если все 4096 символов будут одним словом
                    if to_send.endswith('\n'):  # зачем что то менять если строка заканчивается символом новой строки
                        if len(response) - x < 4096:
                            await try_send(message, to_send)
                        else:
                            await try_send(message, to_send)
                        x += 4096
                        continue
                    while not to_send.endswith('\n'):  # тут смещаем наш срез на столько символов, сколько не являются
                                                       # пробелами
                        to_send = to_send[:-1]
                        x -= 1
                await try_send(message, to_send)
            except Exception as e:
                print(e)
            x += 4096
        await try_send(message, u'\U0001F446' + f'{name} в наличии:', reply_markup=keyboard)
    else:
        try:
            await try_edit(message, response, reply_markup=keyboard)
        except Exception as e:
            print(e)


async def try_send(message: types.Message, response, **kwargs):
    """Попытаться отправить сообщение пользователю"""
    if 'parse_mode' in kwargs:
        parse_mode = kwargs.get('parse_mode')
    else:
        parse_mode = 'Markdown'
    if 'reply_markup' in kwargs:
        try:
            await bot.send_message(message.from_user.id, response, parse_mode=parse_mode, disable_web_page_preview=True,
                                   reply_markup=kwargs.get('reply_markup'))
        except Exception as e:
            print(e)
            return 0
    else:
        try:
            await bot.send_message(message.from_user.id, response, parse_mode=parse_mode, disable_web_page_preview=True)
        except Exception as e:
            print(e)
            return 0
    await sqlite_db.msg_update('botusers', message.from_user.id)
    if 'set_state' in kwargs:
        await kwargs.get('set_state').set()


async def try_edit(message: types.Message, response, **kwargs):
    """Попытаться отредактировать сообщение пользователя"""
    if 'parse_mode' in kwargs:
        parse_mode = kwargs.get('parse_mode')
    else:
        parse_mode = 'Markdown'
    if 'reply_markup' in kwargs:
        try:
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=message['message']['message_id'],
                                        text=response, reply_markup=kwargs.get('reply_markup'), parse_mode=parse_mode,
                                        disable_web_page_preview=True)
        except Exception as e:
            print(e)
            return 0
    else:
        try:
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=message['message']['message_id'],
                                        text=response, parse_mode=parse_mode, disable_web_page_preview=True)
        except Exception as e:
            print(e)
            return 0
    await sqlite_db.msg_update('botusers', message.from_user.id)
    if 'set_state' in kwargs:
        await kwargs.get('set_state').set()


async def try_delete(message: types.Message, offset, long):
    """Попытаться удалить сообщение"""
    try:
        if long == 1:
            await bot.delete_message(chat_id=message['message']['chat']['id'],
                                     message_id=message['message']['message_id'] - offset)
        else:
            await bot.delete_message(chat_id=message['chat']['id'], message_id=message['message_id'] - offset)
    except Exception as e:
        print(e)


def register_handlers_client(dp: Dispatcher):
    """Регистрация хендлеров для клиентской части"""
    with open("config/клавиатуры и типы/buttons.json", 'r', encoding='utf-8') as f:
        all_products_json = f.read()
    all_products = json.loads(all_products_json)
    dp.register_message_handler(command_start, commands=['start'], state='*')
    dp.register_callback_query_handler(actions, text='actions', state='*')
    dp.register_callback_query_handler(actions_alert, text='actions_alert', state='*')
    dp.register_callback_query_handler(actions_previous_page, text='actions_previous_page', state='*')
    dp.register_callback_query_handler(actions_next_page, text='actions_next_page', state='*')
    dp.register_callback_query_handler(go_to_main_actions, text='back_to_main', state='*')
    dp.register_callback_query_handler(bonuses, text='bonuses', state='*')
    dp.register_message_handler(bonuses_login, state=KbPath.Bonus_reg)
    dp.register_callback_query_handler(bonuses_logout, text='log_out', state='*')
    dp.register_callback_query_handler(bonuses_buy_history, text='buy_history', state='*')
    dp.register_callback_query_handler(bonuses_registation_moysklad, text='register_in_bonus', state='*')
    dp.register_callback_query_handler(go_to_main, text='back_to_main', state='*')
    dp.register_callback_query_handler(data_base, text='data_base', state='*')
    dp.register_callback_query_handler(assortiment, text='assortiment', state='*')
    '''кальян'''
    dp.register_callback_query_handler(tabak_assort, text='tabak', state='*')
    dp.register_inline_handler(hookah_search, state=Assortiment.Hookah)
    dp.register_callback_query_handler(coal, text='coal', state='*')
    dp.register_callback_query_handler(chashi, text='chasha', state='*')
    dp.register_callback_query_handler(shipci, text='shipci', state='*')
    dp.register_callback_query_handler(hookahs, text='hookahs', state='*')
    dp.register_callback_query_handler(hookah_complect, text='hookahitems', state='*')
    dp.register_callback_query_handler(service, text='service', state='*')
    dp.register_callback_query_handler(assort_back, text='assort_back', state='*')
    dp.register_callback_query_handler(all_tabak, text='all_tabak', state='*')
    '''кальян'''
    '''табак'''
    for x in all_products["табак"]:
        tabak_d = partial(tabak_types_callback, search=x)
        dp.register_callback_query_handler(tabak_d, text=f'{x}табак', state='*')
    dp.register_callback_query_handler(hookah_back, text='hookah_back', state='*')
    '''табак'''
    '''жидкости'''
    dp.register_callback_query_handler(zidkosti, text='zidkosti', state='*')
    dp.register_inline_handler(vape_search, state=Assortiment.Vape)
    dp.register_callback_query_handler(all_zidkosti, text='all_zizi', state='*')
    for x in all_products["жидкости"]:
        zizi_d = partial(zizi_types_callback, search=x)
        dp.register_callback_query_handler(zizi_d, text=f'{x}жидкости', state='*')
    dp.register_callback_query_handler(vape_back, text='vape_back', state='*')
    '''жидкости'''
    '''устройства'''
    dp.register_callback_query_handler(devices, text='devices', state='*')
    dp.register_callback_query_handler(all_devices, text='all_devices', state='*')
    for x in all_products["устройства"]:
        devices_d = partial(devices_types_callback, search=x)
        dp.register_callback_query_handler(devices_d, text=f'{x}устройства', state='*')
    '''устройства'''
    '''одноразки'''
    dp.register_callback_query_handler(odnorazki, text='odnorazki', state='*')
    dp.register_callback_query_handler(all_odnorazki, text='all_odnorazki', state='*')
    for x in all_products["одноразки"]:
        odnorazki_d = partial(odnorazki_types_callback, search=x)
        dp.register_callback_query_handler(odnorazki_d, text=f'{x}одноразки', state='*')
    '''одноразки'''
    '''расходники'''
    dp.register_callback_query_handler(cartriges, text='cartriges', state='*')
    dp.register_callback_query_handler(all_cartriges, text='all_cartriges', state='*')
    for x in all_products["расходники"]:
        cartriges_d = partial(cartriges_types_callback, search=x)
        dp.register_callback_query_handler(cartriges_d, text=f'{x}расходники', state='*')
    '''расходники'''
    dp.register_callback_query_handler(hookah_assort, text='hookahprod', state='*')
    dp.register_callback_query_handler(vape_assort, text='vapeprod', state='*')
    dp.register_callback_query_handler(via_bot_back, text='via_back', state='*')
    dp.register_inline_handler(assort_search, state='*')
    dp.register_message_handler(main_menu, state='*')
