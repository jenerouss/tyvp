import asyncio
import configparser
import logging
import multiprocessing
import os
import random
import string

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import bot
from data_base import sqlite_db
from handlers import client
from keyboards.admin_kb import *
from loadbase import loadbasemain

logger = logging.getLogger('adminhandlers.admin')


class FSMAdmin(StatesGroup):
    main = State()
    add_hookah = State()
    add_vape = State()
    delete_hookah = State()
    delete_vape = State()
    add_tabak = State()
    add_zizi = State()
    add_odnorazki = State()
    add_devices = State()
    add_cartriges = State()
    delete_tabak = State()
    delete_zizi = State()
    delete_odnorazki = State()
    delete_devices = State()
    delete_cartriges = State()
    shutdown = State()
    update_timer = State()
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    all_sales = json.loads(all_sales_json)
    sale = {}
    salephoto = {}
    for i in range(1, len(all_sales["context"]) + 1):
        sale[i] = State(f'{i}')
    for i in range(1, len(all_sales["context"]) + 1):
        salephoto[i] = State(f'photo{i}')
    newsale_description = State()
    newsale_photo = State()
    sale_add = State()


async def admin_enter(message: types.Message):
    """Вход в админ панель бота
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    await try_send_admin(message, response='Вы в админ моде', reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def admincheck(message: types.Message, state: FSMContext):
    """Проверка на админку
    """
    status = await sqlite_db.check_user_rank('botusers', state, message.from_user.id)
    if status not in ('admin', 'adminplus'):
        await state.finish()
        return 0
    return 1


# Todo: топ 10 самых активных покупателей из бонуски
async def admin_main(message: types.Message, state: FSMContext):
    """Обработчик главного меню админки
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    if message.text == 'Выйти из админ панели':
        await state.finish()
        await client.command_start(message, state)
    if message.text == 'Редактор клавиатур':
        await try_send_admin(message, '||это служебное сообщение, не обращай на него внимание||'
                             , reply_markup=types.ReplyKeyboardRemove(), parse_mode='MarkdownV2')
        await try_delete_admin(message, -1, 0)
        await try_send_admin(message, 'Выберите раздел', reply_markup=kb_admin_kb_redactor)
    if message.text == 'Действия с ботом':
        await try_send_admin(message, '||это служебное сообщение, не обращай на него внимание||'
                             , reply_markup=types.ReplyKeyboardRemove(), parse_mode='MarkdownV2')
        await try_delete_admin(message, -1, 0)
        await bot_actions(message, state)
    if message.text == 'Редактор акций':
        await try_send_admin(message, '||это служебное сообщение, не обращай на него внимание||'
                             , reply_markup=types.ReplyKeyboardRemove(), parse_mode='MarkdownV2')
        await try_delete_admin(message, -1, 0)
        await sales_redactor(message, state)
    if message.text == 'Бд пользователей':
        await try_send_admin(message, '||это служебное сообщение, не обращай на него внимание||'
                             , reply_markup=types.ReplyKeyboardRemove(), parse_mode='MarkdownV2')
        await try_delete_admin(message, -1, 0)
        await users_db(message, state)
    if message.text == 'Статистика':
        await try_send_admin(message, '||это служебное сообщение, не обращай на него внимание||'
                             , reply_markup=types.ReplyKeyboardRemove(), parse_mode='MarkdownV2')
        await try_delete_admin(message, -1, 0)
        await stats(message, state)


async def admin_main_back(message: types.Message, state: FSMContext):
    """Вернуться в главное меню админки
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    await admin_enter(message)


async def kb_buttons_redactor(message: types.Message, state: FSMContext):
    """Редактор кнопок в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    with open("config/клавиатуры и типы/buttons.json", 'r', encoding='utf-8') as f:
        all_types_json = f.read()
    all_types = json.loads(all_types_json)
    response = '"Кнопки клавиатур" - кнопки, которые используются в разделах "ТАБАК, ЖИДКОСТИ, УСТРОЙСТВА, ОДНОРАЗКИ,' \
               'РАСХОДНИКИ УСТРОЙСТВА". Например: в разделе "ТАБАК" есть кнопка "DARKSIDE". Этот раздел предназначен' \
               ' для того, чтобы убирать и добавлять кнопки по типу "DARKSIDE". После добавления/удаления кнопки бота' \
               ' НЕОБХОДИМО перезапустить, чтобы клавиатуры обновились.\nТекущие кнопки:'
    for key, name in all_types.items():
        response += f"\n{key}:\n{name}"
    with open("config/клавиатуры и типы/buttons_backup.json", 'r', encoding='utf-8') as file:
        all_types_json_backup = file.read()
    if all_types_json.lower() == all_types_json_backup.lower():
        response += '\n✅Все кнопки в данный момент отображаются в боте'
    else:
        response += '\n❌В данный момент не все кнопки отображаются в боте. Для отображения всех кнопок, необходим' \
                    ' перезапуск бота'
    await long_msg_admin(message, response, reply_markup=kb_admin_redactor_kb_path_choose)


async def kb_buttons_add_path_choose(message: types.Message, state: FSMContext):
    """Добавление кнопки в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел для добавления'
    await try_send_admin(message, response, reply_markup=kb_admin_redactor_kb_path_choose_add)


async def kb_buttons_add_tabak(message: types.Message, state: FSMContext):
    """Ожидание сообщения для добавления кнопки в табак в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Табак
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название добавляемой кнопки в табак'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_add_path_choose_back)
    await FSMAdmin.add_tabak.set()


async def kb_buttons_add_tabak_confirm(message: types.Message, state: FSMContext):
    """Окончательное добавление кнопки в табак в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Табак
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "табак", True, 'config/клавиатуры и типы/buttons.json') == 'exist':
        await try_send_admin(message, f"{new} уже есть в табак", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()
    elif await write_json(new, "табак", True, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно добавлен в табак", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()


async def kb_buttons_add_zizi(message: types.Message, state: FSMContext):
    """Ожидание сообщения для добавления кнопки в жидкости в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Жидкости
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название добавляемой кнопки в жидкости'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_add_path_choose_back)
    await FSMAdmin.add_zizi.set()


async def kb_buttons_add_zizi_confirm(message: types.Message, state: FSMContext):
    """Окончательное добавление кнопки в жидкости в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Жидкости
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "жидкости", True, 'config/клавиатуры и типы/buttons.json') == 'exist':
        await try_send_admin(message, f"{new} уже есть в жидкости", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()
    elif await write_json(new, "жидкости", True, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно добавлен в жидкости", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()


async def kb_buttons_add_devices(message: types.Message, state: FSMContext):
    """Ожидание сообщения для добавления кнопки в устройства в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Устройства
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название добавляемой кнопки в устройства'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_add_path_choose_back)
    await FSMAdmin.add_devices.set()


async def kb_buttons_add_devices_confirm(message: types.Message, state: FSMContext):
    """Окончательное добавление кнопки в устройства в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Устройства
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "устройства", True, 'config/клавиатуры и типы/buttons.json') == 'exist':
        await try_send_admin(message, f"{new} уже есть в устройства", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()
    elif await write_json(new, "устройства", True, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно добавлен в устройства", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()


async def kb_buttons_add_odnorazki(message: types.Message, state: FSMContext):
    """Ожидание сообщения для добавления кнопки в одноразки в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Одноразки
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название добавляемой кнопки в одноразки'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_add_path_choose_back)
    await FSMAdmin.add_odnorazki.set()


async def kb_buttons_add_odnorazki_confirm(message: types.Message, state: FSMContext):
    """Окончательное добавление кнопки в одноразки в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Одноразки
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "одноразки", True, 'config/клавиатуры и типы/buttons.json') == 'exist':
        await try_send_admin(message, f"{new} уже есть в одноразки", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()
    elif await write_json(new, "одноразки", True, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно добавлен в одноразки", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()


async def kb_buttons_add_cartriges(message: types.Message, state: FSMContext):
    """Ожидание сообщения для добавления кнопки в расходники в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Расходники
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название добавляемой кнопки в расходники'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_add_path_choose_back)
    await FSMAdmin.add_cartriges.set()


async def kb_buttons_add_cartriges_confirm(message: types.Message, state: FSMContext):
    """Окончательное добавление кнопки в расходники в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку -> Расходники
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "расходники", True, 'config/клавиатуры и типы/buttons.json') == 'exist':
        await try_send_admin(message, f"{new} уже есть в расходники", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()
    elif await write_json(new, "расходники", True, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно добавлен в расходники", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()


async def back_to_kb_buttons_redactor(message: types.Message, state: FSMContext):
    """Вернуться в меню редактора кнопок
    Путь: Редактор клавиатур -> Кнопки клавиатур
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    with open("config/клавиатуры и типы/buttons.json", 'r', encoding='utf-8') as f:
        all_types_json = f.read()
    all_types = json.loads(all_types_json)
    response = '"Кнопки клавиатур" - кнопки, которые используются в разделах "ТАБАК, ЖИДКОСТИ, УСТРОЙСТВА, ОДНОРАЗКИ,' \
               'РАСХОДНИКИ УСТРОЙСТВА". Например: в разделе "ТАБАК" есть кнопка "DARKSIDE". Этот раздел предназначен' \
               ' для того, чтобы убирать и добавлять кнопки по типу "DARKSIDE". После добавления/удаления кнопки бота' \
               ' НЕОБХОДИМО перезапустить, чтобы клавиатуры обновились.\nТекущие кнопки:'
    for key, name in all_types.items():
        response += f"\n{key}:\n{name}"
    with open("config/клавиатуры и типы/buttons_backup.json", 'r', encoding='utf-8') as file:
        all_types_json_backup = file.read()
    if all_types_json.lower() == all_types_json_backup.lower():
        response += '\n✅Все кнопки в данный момент отображаются в боте'
    else:
        response += '\n❌В данный момент не все кнопки отображаются в боте. Для отображения всех кнопок, необходим' \
                    ' перезапуск бота'
    await long_msg_admin(message, response, reply_markup=kb_admin_redactor_kb_path_choose)


async def back_to_kb_buttons_add_path_choose(message: types.Message, state: FSMContext):
    """Вернуться в меню добавления кнопок
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Добавить кнопку
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел для добавления'
    await try_send_admin(message, response, reply_markup=kb_admin_redactor_kb_path_choose_add)
    await FSMAdmin.main.set()


async def kb_buttons_delete_path_choose(message: types.Message, state: FSMContext):
    """Удаление кнопки в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел для удаления'
    await try_send_admin(message, response, reply_markup=kb_admin_redactor_kb_path_choose_delete)


async def back_to_kb_buttons_delete_path_choose(message: types.Message, state: FSMContext):
    """Вернуться к меню удаления кнопки в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел для удаления'
    await try_send_admin(message, response, reply_markup=kb_admin_redactor_kb_path_choose_delete)
    await FSMAdmin.main.set()


async def kb_buttons_delete_tabak(message: types.Message, state: FSMContext):
    """Ожидание сообщения для удаления кнопки в табак в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Табак
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название удаляемой кнопки из табак'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_path_delete_choose_back)
    await FSMAdmin.delete_tabak.set()


async def kb_buttons_delete_tabak_confirm(message: types.Message, state: FSMContext):
    """Окончательное удаление кнопки в табак в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Табак
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "табак", False, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно удален из табак", reply_markup=kb_admin_main)
    else:
        await try_send_admin(message, f"{new} нет в табак", reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def kb_buttons_delete_zizi(message: types.Message, state: FSMContext):
    """Ожидание сообщения для удаления кнопки в жидкости в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Жидкости
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название удаляемой кнопки из жидкости'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_path_delete_choose_back)
    await FSMAdmin.delete_zizi.set()


async def kb_buttons_delete_zizi_confirm(message: types.Message, state: FSMContext):
    """Окончательное удаление кнопки в жидкости в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Жидкости
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "жидкости", False, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно удален из жидкости", reply_markup=kb_admin_main)
    else:
        await try_send_admin(message, f"{new} нет в жидкости", reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def kb_buttons_delete_devices(message: types.Message, state: FSMContext):
    """Ожидание сообщения для удаления кнопки в устройства в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Устройства
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название удаляемой кнопки из устройства'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_path_delete_choose_back)
    await FSMAdmin.delete_devices.set()


async def kb_buttons_delete_devices_confirm(message: types.Message, state: FSMContext):
    """Окончательное удаление кнопки в устройства в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Устройства
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "устройства", False, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно удален из устройства", reply_markup=kb_admin_main)
    else:
        await try_send_admin(message, f"{new} нет в устройства", reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def kb_buttons_delete_odnorazki(message: types.Message, state: FSMContext):
    """Ожидание сообщения для удаления кнопки в одноразки в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Одноразки
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название удаляемой кнопки из одноразки'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_path_delete_choose_back)
    await FSMAdmin.delete_odnorazki.set()


async def kb_buttons_delete_odnorazki_confirm(message: types.Message, state: FSMContext):
    """Окончательное удаление кнопки в одноразки в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Одноразки
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "одноразки", False, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно удален из одноразки", reply_markup=kb_admin_main)
    else:
        await try_send_admin(message, f"{new} нет в одноразки", reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def kb_buttons_delete_cartriges(message: types.Message, state: FSMContext):
    """Ожидание сообщения для удаления кнопки в расходники в редакторе клавиатур в админке
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Расходники
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название удаляемой кнопки из расходники'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_kb_path_delete_choose_back)
    await FSMAdmin.delete_cartriges.set()


async def kb_buttons_delete_cartriges_confirm(message: types.Message, state: FSMContext):
    """Окончательное удаление кнопки в расходники в редакторе клавиатур в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Кнопки клавиатур -> Удалить кнопку -> Расходники
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "расходники", False, 'config/клавиатуры и типы/buttons.json'):
        await try_send_admin(message, f"{new} успешно удален из расходники", reply_markup=kb_admin_main)
    else:
        await try_send_admin(message, f"{new} нет в расходники", reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def types_redactor(message: types.Message, state: FSMContext):
    """Редактор типов для поиска через @ в клиентской части, в адмике
    Путь: Редактор клавиатур -> Типы для поиска
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    with open("config/клавиатуры и типы/hookahandvapetypes.json", 'r', encoding='utf-8') as f:
        all_types_json = f.read()
    all_types = json.loads(all_types_json)
    response = '"Типы для поиска" - наименования типов, присвоенных каждому товару в мойсклад. например DARKSIDE - ' \
               'название товара, его тип - ТАБАК.\nЭти типы нигде не отображаются в боте, они нужны для поиска через ' \
               '"@tyvpbot ..."\nДанная функция нужна в случае, если добавился новый тип товара и он не отображается в' \
               ' поиске по кальянной продукции или вейп продукции. Для поиска по всему ассортименту эта функция не ' \
               'требуется. После добавления/удаления любого типа, перезапуск бота НЕ требуется.\nТекущие типы:'
    for key, name in all_types.items():
        response += f"\n{key}:\n{name}"
    await long_msg_admin(message, response, reply_markup=kb_admin_redactor_types_path_choose)


async def back_to_path_choose(message: types.Message, state: FSMContext):
    """Вернуться к выбору в редакторе клавиатур в админке
    Путь: Редактор клавиатур
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел'
    await try_edit_admin(message, response, reply_markup=kb_admin_kb_redactor)


async def types_add_path_choose(message: types.Message, state: FSMContext):
    """Выбор раздела для добавления типа в админке
    Путь: Редактор клавиатур -> Типы для поиска -> Добавить тип
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел для добавления'
    await try_send_admin(message, response, reply_markup=kb_admin_redactor_types_choose_add)


async def back_to_types_redactor(message: types.Message, state: FSMContext):
    """Вернуться к разделу с редактированием типов для поиска
    Путь: Редактор клавиатур -> Типы для поиска
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    with open("config/клавиатуры и типы/hookahandvapetypes.json", 'r', encoding='utf-8') as f:
        all_types_json = f.read()
    all_types = json.loads(all_types_json)
    response = '"Типы для поиска" - наименования типов, присвоенных каждому товару в мойсклад. например DARKSIDE - ' \
               'название товара, его тип - ТАБАК.\nЭти типы нигде не отображаются в боте, они нужны для поиска через ' \
               '"@tyvpbot ..."\nДанная функция нужна в случае, если добавился новый тип товара и он не отображается в' \
               ' поиске по кальянной продукции или вейп продукции. Для поиска по всему ассортименту эта функция не ' \
               'требуется.\nТекущие типы:'
    for key, name in all_types.items():
        response += f"\n{key}:\n{name}"
    await long_msg_admin(message, response, reply_markup=kb_admin_redactor_types_path_choose)


async def types_add_hookah(message: types.Message, state: FSMContext):
    """Ожидание сообщения для добавления типа в раздел кальянной продукции в админке
    Путь: Редактор клавиатур -> Типы для поиска -> Добавить тип -> Кальян
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название добавляемого типа в кальян'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_types_choose_back)
    await FSMAdmin.add_hookah.set()


async def types_add_hookah_confirm(message: types.Message, state: FSMContext):
    """Окончательное добавление типа в раздел кальянной продукции в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Типы для поиска -> Добавить тип -> Кальян
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "кальян", True, 'config/клавиатуры и типы/hookahandvapetypes.json') == 'exist':
        await try_send_admin(message, f"{new} уже есть в кальян", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()
    elif await write_json(new, "кальян", True, 'config/клавиатуры и типы/hookahandvapetypes.json'):
        await try_send_admin(message, f"{new} успешно добавлен в кальян", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()


async def types_add_vape(message: types.Message, state: FSMContext):
    """Ожидание сообщения для добавления типа в раздел вейп продукции в админке
    Путь: Редактор клавиатур -> Типы для поиска -> Добавить тип -> Вейп
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название добавляемого типа в вейп'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_types_choose_back)
    await FSMAdmin.add_vape.set()


async def types_add_vape_confirm(message: types.Message, state: FSMContext):
    """Окончательное добавление типа в раздел вейп продукции в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Типы для поиска -> Добавить тип -> Вейп
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "вейп", True, 'config/клавиатуры и типы/hookahandvapetypes.json') == 'exist':
        await try_send_admin(message, f"{new} уже есть в вейп", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()
    elif await write_json(new, "вейп", True, 'config/клавиатуры и типы/hookahandvapetypes.json'):
        await try_send_admin(message, f"{new} успешно добавлен в вейп", reply_markup=kb_admin_main)
        await FSMAdmin.main.set()


async def back_to_types_add_path_choose(message: types.Message, state: FSMContext):
    """Вернуться к выбору раздела в добавлении типа в редакторе типов для поиска в админке
    Путь: Редактор клавиатур -> Типы для поиска -> Добавить тип
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел для добавления'
    await try_send_admin(message, response, reply_markup=kb_admin_redactor_types_choose_add)
    await FSMAdmin.main.set()


async def back_to_types_delete_path_choose(message: types.Message, state: FSMContext):
    """Вернуться к выбору раздела в удаление типа в редакторе типов для поиска в админке
    Путь: Редактор клавиатур -> Типы для поиска -> Удалить тип
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел для удаления'
    await try_send_admin(message, response, reply_markup=kb_admin_redactor_types_choose_delete)
    await FSMAdmin.main.set()


async def types_delete_path_choose(message: types.Message, state: FSMContext):
    """Выбор раздела для удаления типа в админке
    Путь: Редактор клавиатур -> Типы для поиска -> Удалить тип
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите раздел для удаления'
    await try_send_admin(message, response, reply_markup=kb_admin_redactor_types_choose_delete)


async def types_delete_hookah(message: types.Message, state: FSMContext):
    """Ожидание сообщения для удаления типа из раздела кальянной продукции в админке
    Путь: Редактор клавиатур -> Типы для поиска -> Удалить тип -> Кальян
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название типа, который хотите удалить из кальян'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_types_choose_back)
    await FSMAdmin.delete_hookah.set()


async def types_delete_vape(message: types.Message, state: FSMContext):
    """Ожидание сообщения для удаления типа из раздела вейп продукции в админке
    Путь: Редактор клавиатур -> Типы для поиска -> Удалить тип -> Вейп
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Введите название типа, который хотите удалить из вейп'
    await try_edit_admin(message, response, reply_markup=kb_admin_redactor_types_choose_back)
    await FSMAdmin.delete_vape.set()


async def types_delete_hookah_confirm(message: types.Message, state: FSMContext):
    """Окончательное удаление типа из раздела кальян продукции в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Типы для поиска -> Удалить тип -> Кальян
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "кальян", False, 'config/клавиатуры и типы/hookahandvapetypes.json'):
        await try_send_admin(message, f"{new} успешно удален из кальян", reply_markup=kb_admin_main)
    else:
        await try_send_admin(message, f"{new} нет в кальян", reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def types_delete_vape_confirm(message: types.Message, state: FSMContext):
    """Окончательное удаление типа из раздела вейп продукции в админке,
    функция работает после отправки сообщения в боте по пути ниже
    Путь: Редактор клавиатур -> Типы для поиска -> Удалить тип -> Вейп
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    new = message.text
    if await write_json(new, "вейп", False, 'config/клавиатуры и типы/hookahandvapetypes.json'):
        await try_send_admin(message, f"{new} успешно удален из вейп", reply_markup=kb_admin_main)
    else:
        await try_send_admin(message, f"{new} нет в вейп", reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def bot_actions(message: types.Message, state: FSMContext):
    """Действия с ботом в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите действие.\nПерезапуск бота лучше делать в ночное время, когда ботом никто не пользуется.' \
               'После выключения бота, включить его можно будет только вручную на сервере.Выключение бота нужно при' \
               ' критических ошибках или серьезных проблемах'
    await try_send_admin(message, response, reply_markup=kb_admin_bot_actions)


async def bot_restart(message: types.Message, state: FSMContext):
    """Ожидание подтверждения на рестарт бота в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Перезапустить бота? Когда бот запустится, вам придет сообщение'
    await try_edit_admin(message, response, reply_markup=kb_admin_restart_bot)


async def bot_restart_confirm(message: types.Message, state: FSMContext):
    """Рестарт бота в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Перезапускаю бота.'
    await try_send_admin(message, response)
    state.storage.data['__restart_id'].value = message.from_user.id
    state.storage.data['__shutdown_event'].value = 0
    state.storage.data['__restart_event'].set()


async def bot_shutdown(message: types.Message, state: FSMContext):
    """Ожидание подтверждения для выключения бота в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Для ❗️_Выключения_❗️ бота, введите следующий текст:\n'
    shutdown_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    with open('config/shutdown_key.txt', 'w', encoding='utf-8') as f:
        f.write(shutdown_key)
    response += shutdown_key
    await FSMAdmin.shutdown.set()
    await try_edit_admin(message, response, reply_markup=kb_admin_shutdown)


async def back_to_bot_actions(message: types.Message, state: FSMContext):
    """Вернуться к действиям с ботом в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Выберите действие.\nПерезапуск бота лучше делать в ночное время, когда ботом никто не пользуется.' \
               'После выключения бота, включить его можно будет только вручную на сервере.Выключение бота нужно при' \
               ' критических ошибках или серьезных проблемах'
    await try_edit_admin(message, response, reply_markup=kb_admin_bot_actions)
    await FSMAdmin.main.set()


async def bot_shutdown_confirm(message: types.Message, state: FSMContext):
    """Выключение бота в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    with open('config/shutdown_key.txt', 'r', encoding='utf-8') as f:
        shutdown_key = f.read()
    if message.text == str(shutdown_key):
        response = 'Выключаю бота'
        await try_send_admin(message, response)
        state.storage.data['__shutdown_event'].value = 1
        state.storage.data['__restart_event'].set()
    else:
        response = 'Введенный текст не совпадает с необходимым для выключения'
        await try_send_admin(message, response, reply_markup=kb_admin_shutdown)


async def back_to_bot_shutdown(message: types.Message, state: FSMContext):
    """Вернуться к подтверждению выключения бота в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Для ❗️_Выключения_❗️ бота, введите следующий текст:\n'
    shutdown_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    with open('config/shutdown_key.txt', 'w', encoding='utf-8') as f:
        f.write(shutdown_key)
    response += shutdown_key
    await FSMAdmin.shutdown.set()
    await try_edit_admin(message, response, reply_markup=kb_admin_shutdown)


async def moysklad(message: types.Message, state: FSMContext):
    """Меню для взаимодействия с базой данных мойсклад в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'В этом меню вы можете принудительно обновить базу данных МойСклад и поменять таймер автоматического' \
               ' обновления базы данных МойСклад'
    await try_edit_admin(message, response, reply_markup=kb_admin_moysklad)
    await FSMAdmin.main.set()


async def moysklad_update(message: types.Message, state: FSMContext):
    """Запустить принудительное обновление базы данных мойсклад в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    await try_send_admin(message, response='Запускаю обновление базы данных Мойсклад.', reply_markup=kb_admin_main)
    update_proc = multiprocessing.Process(target=moysklad_call)
    update_proc.start()


def moysklad_call():
    """Вызов обновления бд мойсклад
    """
    asyncio.run(loadbasemain.load(force_load=True))
    multiprocessing.current_process().close()


async def moysklad_update_timer(message: types.Message, state: FSMContext):
    """Редактор таймера обновления бд мойсклад в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    config = configparser.ConfigParser()
    config.read('config/settings.ini')
    time_to_load = int(config['DB']['data_base_load_timer_seconds']) / 60
    response = 'Введите желаемое количество минут для обновления базы данных МойСклад.\nВ данный момент таймер ' \
               f'обновления базы данных МойСклад равен {str(time_to_load)[:-2]} минутам'
    await try_edit_admin(message, response, reply_markup=kb_admin_update_moysklad_back)
    await FSMAdmin.update_timer.set()


async def moysklad_update_timer_confirm(message: types.Message, state: FSMContext):
    """Изменение таймера обновления бд мойсклад в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    update_timer = int(message.text)
    if update_timer < 1 or update_timer > 35791394:
        await try_send_admin(message, 'Значение должно являться числом и быть больше либо равно 1 и меньше 35791394',
                             reply_markup=kb_admin_update_moysklad_back)
        return
    config = configparser.ConfigParser()
    config.read('config/settings.ini')
    config['DB']['data_base_load_timer_seconds'] = str(update_timer * 60)
    with open('config/settings.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    state.storage.data['__sleep_time'].value = update_timer * 60
    await try_send_admin(message, f'Значение таймера обновлено: {str(update_timer)} минут', reply_markup=kb_admin_main)
    await FSMAdmin.main.set()


async def sales_redactor(message: types.Message, state: FSMContext):
    """Редактор акций в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    await FSMAdmin.main.set()
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    all_sales = json.loads(all_sales_json)
    count_active = 0
    for i in all_sales['context']:
        if i['action']['active'] == '1':
            count_active += 1
    count_all = len(all_sales['context'])
    response = f'Здесь вы можете изменить текущие акции, удалять и добавлять новые акции\nВсего акций в базе: ' \
               f'{count_all},\nИз них отображаются: {count_active}'
    await try_send_admin(message, response, reply_markup=kb_admin_sales)


async def admin_photo_send(message: types.Message, state: FSMContext, photo_path, caption, keyboard):
    """Отправка фото в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    try:
        await bot.send_photo(chat_id=message.from_user.id, photo=open(photo_path, 'rb'), caption=caption,
                             reply_markup=keyboard, parse_mode='Markdown')
    except Exception as e:
        print(e)


async def sales_list_previous_page(message: types.Message):
    """Вернуться на предыдущую страницу в редакторе акций в админке
    """
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    current_page = int(message['message']['reply_markup']['inline_keyboard'][0][1]['text'].split('/')[0][9:])
    all_sales = json.loads(all_sales_json)
    photo_paths = []
    captions = []
    max_actions = len(all_sales['context'])
    for i in range(len(all_sales['context'])):
        photo_paths.append(all_sales['context'][i]['action']['photo_path'])
        if all_sales['context'][i]['action']['active'] == "0":
            captions.append(f"Описание: {all_sales['context'][i]['action']['caption']}\nАкция неактивна\nДля "
                            f"корректной работы акций в пользовательском меню, после выключения или включения "
                            f"определенной акции, боту нужен перезапуск. После нажатия кнопки 'Вкл/Выкл акцию', бот "
                            f"автоматически перезапустится. Новое описание или фотография сразу же будут корректно "
                            f"отображаться в пользовательском меню")
        else:
            captions.append(f"Описание: {all_sales['context'][i]['action']['caption']}\nАкция активна\nДля "
                            f"корректной работы акций в пользовательском меню, после выключения или включения "
                            f"определенной акции, боту нужен перезапуск. После нажатия кнопки 'Вкл/Выкл акцию', бот "
                            f"автоматически перезапустится. Новое описание или фотография сразу же будут корректно "
                            f"отображаться в пользовательском меню")
    if current_page == max_actions:
        await bot.edit_message_media(media=types.InputMedia(
            media=open(photo_paths[current_page - 2], 'rb'),
            caption=captions[current_page - 2]),
            chat_id=message.from_user.id, message_id=message['message']['message_id'],
            reply_markup=kbs_admin_sales_list[current_page - 2])
    else:
        await bot.edit_message_media(media=types.InputMedia(
            media=open(photo_paths[current_page - 2], 'rb'),
            caption=captions[current_page - 2]),
            chat_id=message.from_user.id, message_id=message['message']['message_id'],
            reply_markup=kbs_admin_sales_list[current_page - 2])


async def sales_list_first_page(message: types.Message, state: FSMContext):
    """Первая страница в редакторе акций в админке
    """
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    all_sales = json.loads(all_sales_json)
    photo_path = all_sales['context'][0]['action']['photo_path']
    if all_sales['context'][0]['action']['active'] == "0":
        caption = (f"Описание: {all_sales['context'][0]['action']['caption']}\nАкция неактивна\n_Для "
                            f"корректной работы акций в пользовательском меню, после выключения или включения "
                            f"определенной акции, боту нужен перезапуск. После нажатия кнопки _*Вкл/Выкл акцию*_, бот "
                            f"автоматически перезапустится. Новое описание или фотография сразу же будут корректно "
                            f"отображаться в пользовательском меню_")
    else:
        caption = (f"Описание: {all_sales['context'][0]['action']['caption']}\nАкция активна\n_Для "
                            f"корректной работы акций в пользовательском меню, после выключения или включения "
                            f"определенной акции, боту нужен перезапуск. После нажатия кнопки _*Вкл/Выкл акцию*_, бот "
                            f"автоматически перезапустится. Новое описание или фотография сразу же будут корректно "
                            f"отображаться в пользовательском меню_")
    await admin_photo_send(message, state, photo_path=photo_path, caption=caption,
                           keyboard=kbs_admin_sales_list[0])


async def sales_list_alert(callback_query: types.CallbackQuery):
    """Уведомление по нажатию кнопки 'Страница */*' в редакторе акций в админке
    """
    page = callback_query["message"]["reply_markup"]["inline_keyboard"][0][1]["text"]
    try:
        await bot.answer_callback_query(callback_query.id, text=page,
                                        show_alert=False)
    except Exception as e:
        print(e)


async def sales_list_next_page(message: types.Message):
    """Перейти к следующей странице в редакторе акций в админке
    """
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    current_page = int(message['message']['reply_markup']['inline_keyboard'][0][1]['text'].split('/')[0][9:])
    all_sales = json.loads(all_sales_json)
    photo_paths = []
    captions = []
    max_actions = len(all_sales['context'])
    for i in range(len(all_sales['context'])):
        photo_paths.append(all_sales['context'][i]['action']['photo_path'])
        if all_sales['context'][i]['action']['active'] == "0":
            captions.append(f"Описание: {all_sales['context'][i]['action']['caption']}\nАкция неактивна\nДля "
                            f"корректной работы акций в пользовательском меню, после выключения или включения "
                            f"определенной акции, боту нужен перезапуск. После нажатия кнопки 'Вкл/Выкл акцию', бот "
                            f"автоматически перезапустится. Новое описание или фотография сразу же будут корректно "
                            f"отображаться в пользовательском меню")
        else:
            captions.append(f"Описание: {all_sales['context'][i]['action']['caption']}\nАкция активна\nДля "
                            f"корректной работы акций в пользовательском меню, после выключения или включения "
                            f"определенной акции, боту нужен перезапуск. После нажатия кнопки 'Вкл/Выкл акцию', бот "
                            f"автоматически перезапустится. Новое описание или фотография сразу же будут корректно "
                            f"отображаться в пользовательском меню")
    if current_page == max_actions:
        await bot.edit_message_media(media=types.InputMedia(
            media=open(photo_paths[0], 'rb'),
            caption=captions[0]),
            chat_id=message.from_user.id, message_id=message['message']['message_id'],
            reply_markup=kbs_admin_sales_list[0])
    else:
        await bot.edit_message_media(media=types.InputMedia(
            media=open(photo_paths[current_page], 'rb'),
            caption=captions[current_page]),
            chat_id=message.from_user.id, message_id=message['message']['message_id'],
            reply_markup=kbs_admin_sales_list[current_page])


async def sales_list_set_page(message: types.Message, state: FSMContext, page: int):
    """Функция для корректного отображения текста в редакторе акций в админе
    В зависимости от того, активная акция или нет, текст на странице меняется
    """
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    all_sales = json.loads(all_sales_json)
    photo_path = (all_sales['context'][page]['action']['photo_path'])
    if all_sales['context'][page]['action']['active'] == "0":
        caption = (f"Описание: {all_sales['context'][page]['action']['caption']}\nАкция неактивна\n_Для "
                            f"корректной работы акций в пользовательском меню, после выключения или включения "
                            f"определенной акции, боту нужен перезапуск. После нажатия кнопки _*Вкл/Выкл акцию*_, бот "
                            f"автоматически перезапустится. Новое описание или фотография сразу же будут корректно "
                            f"отображаться в пользовательском меню_")
    else:
        caption = (f"Описание: {all_sales['context'][page]['action']['caption']}\nАкция активна\n_Для "
                            f"корректной работы акций в пользовательском меню, после выключения или включения "
                            f"определенной акции, боту нужен перезапуск. После нажатия кнопки _*Вкл/Выкл акцию*_, бот "
                            f"автоматически перезапустится. Новое описание или фотография сразу же будут корректно "
                            f"отображаться в пользовательском меню_")
    await admin_photo_send(message, state, photo_path=photo_path, caption=caption,
                           keyboard=kbs_admin_sales_list[page])


async def sales_caption_redactor(message: types.Message, state: FSMContext):
    """Редактор описания акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    page = message["message"]["reply_markup"]["inline_keyboard"][0][1]["text"][9:-2]
    response = 'Введите новое описание акции:'
    await try_send_admin(message, response, reply_markup=kb_admin_sales_list_back)
    await FSMAdmin.sale[int(page)].set()


async def sales_back_to_pages_desc(message: types.Message, state: FSMContext):
    """Вернуться из редактора описания акции к редактору акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    current_page = await state.get_state()
    current_page = int(current_page[2:]) - 1
    await FSMAdmin.main.set()
    await sales_list_set_page(message, state, current_page)


async def sales_back_to_pages_photo(message: types.Message, state: FSMContext):
    """Вернуться из редактора фото акции к редактору акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    current_page = await state.get_state()
    current_page = int(current_page[7:]) - 1
    await FSMAdmin.main.set()
    await sales_list_set_page(message, state, current_page)


async def sales_caption_redactor_confirm(message: types.Message, state: FSMContext):
    """Окончательное изменение описания акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s текст: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username, message.text)
    if not await admincheck(message, state):
        return
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    all_sales = json.loads(all_sales_json)
    current_page = await state.get_state()
    current_page = int(current_page[2:]) - 1
    all_sales["context"][current_page]["action"]["caption"] = message.text
    with open('config/акции/actions.json', 'w', encoding="utf-8") as f:
        json.dump(all_sales, f, indent=4, ensure_ascii=False)
    await FSMAdmin.main.set()
    await sales_list_set_page(message, state, current_page)


async def sales_photo_redactor(message: types.Message, state: FSMContext):
    """Редактор фото в редакторе акций в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    page = int(message["message"]["reply_markup"]["inline_keyboard"][0][1]["text"][9:-2])
    response = 'Отправьте фотографию, которую хотите установить для акции. Внимание: текущая фотография не будет ' \
               'сохранена, если не хотите ее потерять, то лучше сохраните ее сейчас'
    await try_send_admin(message, response, reply_markup=kb_admin_sales_list_back)
    await FSMAdmin.salephoto[page].set()


async def sales_photo_err(message: types.Message, state: FSMContext):
    """Уведомление о том, что админ отправил текст вместо фото в редакторе фото акции в админке"""
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    await try_send_admin(message, 'Ожидаю фотографию для акции, а не текст', reply_markup=kb_admin_sales_list_back)


async def sales_add(message: types.Message, state: FSMContext):
    """Добавление новой акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    if os.path.exists('config/акции/actions_add.json'):
        os.remove('config/акции/actions_add.json')
    await try_send_admin(message, 'Введите описание добавляемой акции', reply_markup=kb_admin_sales_list_back)
    await FSMAdmin.newsale_description.set()


async def sales_add_description(message: types.Message, state: FSMContext):
    """Добавление описания для новой акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    sale_write = {"action": {"caption": message.text, "photo_path": "", "active": "0"}}
    with open("config/акции/actions_add.json", 'w', encoding='utf-8') as f:
        json.dump(sale_write, f, indent=4, ensure_ascii=False)
    await try_send_admin(message, 'Отправьте фото добавляемой акции', reply_markup=kb_admin_sales_list_back)
    await FSMAdmin.newsale_photo.set()


async def sales_add_photo(message: types.Message, state: FSMContext):
    """Ожидание добавления фото для новой акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        sale_json = f.read()
    sale = json.loads(sale_json)
    current_page = len(sale["context"])
    dest_file = f'config/акции/картинки для акций/photo-{current_page + 1}.jpg'
    await message.photo[-1].download(destination_file=dest_file)
    with open("config/акции/actions_add.json", 'r', encoding='utf-8') as f:
        newsale_json = f.read()
    newsale = json.loads(newsale_json)
    newsale["action"]["photo_path"] = dest_file
    with open("config/акции/actions_add.json", 'r+', encoding='utf-8') as f:
        json.dump(newsale, f, indent=4, ensure_ascii=False)
    await try_send_admin(message, 'После добавления акции, бот автоматически перезапустится. '
                                  'Акция по умолчанию будет неактивной.\nНовая акция будет выглядеть так:')
    await admin_photo_send(message, state, newsale["action"]["photo_path"], newsale["action"]['caption'],
                           keyboard=kb_admin_sale_add)
    await FSMAdmin.sale_add.set()


async def sales_add_photo_confirm(message: types.Message, state: FSMContext):
    """Окончательное добавление фото для новой акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        sale_json = f.read()
    sale = json.loads(sale_json)
    current_page = len(sale["context"])
    dest_file = f'config/акции/картинки для акций/photo-{current_page + 1}.jpg'
    with open("config/акции/actions_add.json", 'r', encoding='utf-8') as f:
        newsale_json = f.read()
    newsale = json.loads(newsale_json)
    newsale["action"]["photo_path"] = dest_file
    sale["context"].append(newsale)
    with open("config/акции/actions.json", 'r+', encoding='utf-8') as f:
        json.dump(sale, f, indent=4, ensure_ascii=False)
    if os.path.exists('config/акции/actions_add.json'):
        os.remove('config/акции/actions_add.json')
    await bot_restart_confirm(message, state)


async def sales_photo_confirm(message: types.Message, state: FSMContext):
    """Изменение фото в уже существующей акции в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    current_page = await state.get_state()
    current_page = int(current_page[7:]) - 1
    dest_file = f'config/акции/картинки для акций/photo-{current_page + 1}.jpg'
    await message.photo[-1].download(destination_file=dest_file)
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    all_sales = json.loads(all_sales_json)
    all_sales["context"][current_page]["action"]["photo_path"] = dest_file
    with open('config/акции/actions.json', 'w', encoding="utf-8") as f:
        json.dump(all_sales, f, indent=4, ensure_ascii=False)
    await FSMAdmin.main.set()
    await sales_list_set_page(message, state, current_page)


async def sales_switch(message: types.Message, state: FSMContext):
    """Переключение отображения акции для клиентской части в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    all_sales = json.loads(all_sales_json)
    page = int(message["message"]["reply_markup"]["inline_keyboard"][0][1]["text"][9:-2]) - 1
    if all_sales["context"][page]["action"]["active"] == '1':
        all_sales["context"][page]["action"]["active"] = '0'
    elif all_sales["context"][page]["action"]["active"] == '0':
        all_sales["context"][page]["action"]["active"] = '1'
    with open('config/акции/actions.json', 'w', encoding="utf-8") as f:
        json.dump(all_sales, f, indent=4, ensure_ascii=False)
    await sales_list_set_page(message, state, page)
    await bot_restart_confirm(message, state)


async def users_db(message: types.Message, state: FSMContext):
    """Бд пользователей в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Здесь вы можете посмотреть всех пользователей, зарегистрированных в бонуске в МойСклад, а так же всех' \
               ' пользователей данного бота.'
    await try_send_admin(message, response, reply_markup=kb_admin_users_db)


async def users_db_back(message: types.Message, state: FSMContext):
    """Вернуться к бд пользователей в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    response = 'Здесь вы можете посмотреть всех пользователей, зарегистрированных в бонуске в МойСклад, а так же всех' \
               ' пользователей данного бота.'
    await try_edit_admin(message, response, reply_markup=kb_admin_users_db)


async def moysklad_users_db(message: types.Message, state: FSMContext):
    """Вывод всех пользователей бонуски в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    users = await sqlite_db.data_from_sql('bonususers', 'name', '', phone_format=True)
    to_send = ''
    all_types = []
    for i in range(len(users)):
        all_types.append({
            'name': users[i][1],
            'phone': users[i][0],
            'bonusPoints': users[i][3],
            'salesAmount': users[i][2],
        })
    all_types.sort(key=lambda person: person['salesAmount'])
    for i, person in enumerate(all_types):
        to_send += f'{i + 1})\n{person["name"]}\n{person["phone"]}\n{person["bonusPoints"]} ' \
                f'баллов\n{person["salesAmount"]} р. - сумма покупок\n\n'
    await long_msg_admin(message, to_send, reply_markup=kb_admin_users_db_back)


async def bot_db_output(message: types.Message, state: FSMContext):
    """Вывод всех пользователей бота в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    users = await sqlite_db.data_from_sql('botusers', 'id', '', phone_format=True)
    to_send = ''
    all_types = []
    for i in range(len(users)):
        all_types.append({
            'id': users[i][0],
            'name': users[i][1],
            'number': users[i][2],
            'username': users[i][3],
            'status': users[i][4],
            'activity': users[i][5],
            'last_activity': users[i][6],
            'registration_date': users[i][7],
        })
    all_types.sort(key=lambda person: person['status'])
    for i, person in enumerate(all_types):
        to_send += f'{i + 1})\n{person["id"]} - айди в тг\n{person["name"]} - имя в бонуске\n{person["number"]} - ' \
                   f'телефон в бонуске\n{person["username"]} - ник в тг\n{person["status"]} - ранг\n{person["activity"]}' \
                   f' - активность\n{person["last_activity"]} - последняя активность\n{person["registration_date"]}' \
                   f' - дата регистрации\n\n'
    await long_msg_admin(message, to_send, reply_markup=kb_admin_users_db_back)


# Todo:
async def stats(message: types.Message, state: FSMContext):
    """Статистика в админке
    """
    logger.info('айди: %d имя: %s ник: %s', message.from_user.id,
                message.from_user.full_name, message.from_user.username)
    if not await admincheck(message, state):
        return
    await try_send_admin(message, response='В разработке', reply_markup=kb_admin_main)


async def write_json(new_data, add_type, add, filename):
    """кастом запись в json файл
    """
    try:
        with open(filename, 'r+', encoding="utf-8") as file:
            file_data = json.load(file)
            if add:
                for i in range(len(file_data[add_type])):
                    if file_data[add_type][i].lower() == new_data.lower():
                        return 'exist'
                file_data[add_type].append(new_data)
            else:
                for i in range(len(file_data[add_type])):
                    if file_data[add_type][i].lower() == new_data.lower():
                        file_data[add_type].pop(i)
                        break
                else:
                    return False
            with open(filename, 'w', encoding="utf-8") as f:
                json.dump(file_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(e)
        return False


async def try_send_admin(message: types.Message, response: str, **kwargs):
    """Попытаться отправить сообщение в админке
    """
    if 'parse_mode' in kwargs:
        parse_mode = kwargs.get('parse_mode')
    else:
        parse_mode = 'Markdown'
    if 'reply_markup' in kwargs:
        try:
            await bot.send_message(message.from_user.id, response, parse_mode=parse_mode,
                                   reply_markup=kwargs.get('reply_markup'))
        except Exception as e:
            print(e)
    else:
        try:
            await bot.send_message(message.from_user.id, response, parse_mode=parse_mode)
        except Exception as e:
            print(e)


async def try_edit_admin(message: types.Message, response, **kwargs):
    """Попытаться отредактировать сообщение в админке
    """
    if 'reply_markup' in kwargs:
        try:
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=message['message']['message_id'],
                                        text=response, reply_markup=kwargs.get('reply_markup'), parse_mode='Markdown',
                                        disable_web_page_preview=True)
        except Exception as e:
            print(e)
            return 0
    else:
        try:
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=message['message']['message_id'],
                                        text=response, parse_mode='Markdown', disable_web_page_preview=True)
        except Exception as e:
            print(e)
            return 0


# Todo: не забыть перенести в клиенстскую часть в случае одобрения
async def long_msg_admin(message: types.Message, response, **kwargs):
    """Отправка длинного текста несколькими сообщениями в админке"""
    if len(response) > 4096:
        x = 0
        while x < len(response):
            try:
                to_send = response[x:x + 4096]  # Делаем срез по ограничениям телеги
                if ' ' in to_send:  # такое вряд ли будет, но это на случай, если все 4096 символов будут одним словом
                    if to_send.endswith('\n'):  # зачем что то менять если строка заканчивается символом новой строки
                        if len(response) - x < 4096:
                            await try_send_admin(message, to_send, reply_markup=kwargs.get('reply_markup'))
                        else:
                            await try_send_admin(message, to_send)
                        x += 4096
                        continue
                    while not to_send.endswith(' '):  # тут смещаем наш срез на столько символов, сколько не являются
                                                      # пробелами
                        to_send = to_send[:-1]
                        x -= 1
                await try_send_admin(message, to_send)
            except Exception as e:
                print(e)
            x += 4096
    else:
        if 'reply_markup' in kwargs:
            try:
                await try_edit_admin(message, response, reply_markup=kwargs.get('reply_markup'))
            except Exception as e:
                print(e)
        else:
            try:
                await try_edit_admin(message, response)
            except Exception as e:
                print(e)


async def try_delete_admin(message: types.Message, offset, long):
    """Попытаться удалить сообщение в админке"""
    try:
        if long == 1:
            await bot.delete_message(chat_id=message['message']['chat']['id'],
                                     message_id=message['message']['message_id'] - offset)
        else:
            await bot.delete_message(chat_id=message['chat']['id'], message_id=message['message_id'] - offset)
    except Exception as e:
        print(e)


def register_handlers_admin(dp: Dispatcher):
    """Регистрация хендлеров для админки"""
    dp.register_callback_query_handler(admin_main_back, text='path_choose_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_redactor, text='kb_buttons', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_add_path_choose, text='add_button', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_add_tabak, text='add_button_tabak', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_add_zizi, text='add_button_zizi', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_add_cartriges, text='add_button_cartriges', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_add_devices, text='add_button_devices', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_add_odnorazki, text='add_button_odnorazki', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_kb_buttons_redactor, text='kb_redactor_types_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_kb_buttons_add_path_choose, text='redactor_kb_add_path_choose_back',
                                       state=FSMAdmin.add_tabak)
    dp.register_callback_query_handler(back_to_kb_buttons_add_path_choose, text='redactor_kb_add_path_choose_back',
                                       state=FSMAdmin.add_zizi)
    dp.register_callback_query_handler(back_to_kb_buttons_add_path_choose, text='redactor_kb_add_path_choose_back',
                                       state=FSMAdmin.add_cartriges)
    dp.register_callback_query_handler(back_to_kb_buttons_add_path_choose, text='redactor_kb_add_path_choose_back',
                                       state=FSMAdmin.add_devices)
    dp.register_callback_query_handler(back_to_kb_buttons_add_path_choose, text='redactor_kb_add_path_choose_back',
                                       state=FSMAdmin.add_odnorazki)
    dp.register_callback_query_handler(kb_buttons_delete_path_choose, text='delete_button', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_delete_tabak, text='delete_button_tabak', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_delete_zizi, text='delete_button_zizi', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_delete_cartriges, text='delete_button_cartriges', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_delete_devices, text='delete_button_devices', state=FSMAdmin.main)
    dp.register_callback_query_handler(kb_buttons_delete_odnorazki, text='delete_button_odnorazki', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_kb_buttons_redactor, text='kb_redactor_types_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_kb_buttons_delete_path_choose, text='redactor_kb_path_delete_choose_back',
                                       state=FSMAdmin.delete_tabak)
    dp.register_callback_query_handler(back_to_kb_buttons_delete_path_choose, text='redactor_kb_path_delete_choose_back',
                                       state=FSMAdmin.delete_zizi)
    dp.register_callback_query_handler(back_to_kb_buttons_delete_path_choose, text='redactor_kb_path_delete_choose_back',
                                       state=FSMAdmin.delete_cartriges)
    dp.register_callback_query_handler(back_to_kb_buttons_delete_path_choose, text='redactor_kb_path_delete_choose_back',
                                       state=FSMAdmin.delete_devices)
    dp.register_callback_query_handler(back_to_kb_buttons_delete_path_choose, text='redactor_kb_path_delete_choose_back',
                                       state=FSMAdmin.delete_odnorazki)
    dp.register_callback_query_handler(types_redactor, text='search_types', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_path_choose, text='search_types_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(types_add_path_choose, text='add_type', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_types_redactor, text='search_types_add_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(types_add_hookah, text='hookah_add', state=FSMAdmin.main)
    dp.register_callback_query_handler(types_add_vape, text='vape_add', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_types_add_path_choose, text='search_types_add_choose_back',
                                       state=FSMAdmin.add_vape)
    dp.register_callback_query_handler(back_to_types_add_path_choose, text='search_types_add_choose_back',
                                       state=FSMAdmin.add_hookah)
    dp.register_callback_query_handler(back_to_types_delete_path_choose, text='search_types_add_choose_back',
                                       state=FSMAdmin.delete_vape)
    dp.register_callback_query_handler(back_to_types_delete_path_choose, text='search_types_add_choose_back',
                                       state=FSMAdmin.delete_hookah)
    dp.register_callback_query_handler(types_delete_path_choose, text='delete_type', state=FSMAdmin.main)
    dp.register_callback_query_handler(types_delete_hookah, text='hookah_delete', state=FSMAdmin.main)
    dp.register_callback_query_handler(types_delete_vape, text='vape_delete', state=FSMAdmin.main)
    dp.register_callback_query_handler(bot_restart, text='restart_bot', state=FSMAdmin.main)
    dp.register_callback_query_handler(bot_restart_confirm, text='restart_bot_yes', state=FSMAdmin.main)
    dp.register_callback_query_handler(bot_shutdown, text='shutdown_bot', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_bot_actions, text='restart_bot_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(admin_main_back, text='bot_actions_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_bot_actions, text='shutdown_back', state=FSMAdmin.shutdown)
    dp.register_callback_query_handler(back_to_bot_shutdown, text='shutdown_confirm_back', state=FSMAdmin.shutdown)
    dp.register_callback_query_handler(moysklad, text='moysklad', state=FSMAdmin.main)
    dp.register_callback_query_handler(moysklad_update, text='update_moysklad', state=FSMAdmin.main)
    dp.register_callback_query_handler(back_to_bot_actions, text='moysklad_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(moysklad_update_timer, text='update_moysklad_timer', state=FSMAdmin.main)
    dp.register_callback_query_handler(moysklad, text='update_moysklad_back', state=FSMAdmin.update_timer)
    dp.register_callback_query_handler(admin_main_back, text='admin_sales_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(sales_list_first_page, text='admin_sales_list_view', state=FSMAdmin.main)
    dp.register_callback_query_handler(sales_list_next_page, text='admin_sales_list_next_page', state=FSMAdmin.main)
    dp.register_callback_query_handler(sales_list_previous_page, text='admin_sales_list_previous_page',
                                       state=FSMAdmin.main)
    dp.register_callback_query_handler(sales_list_alert, text='admin_sales_list_alert', state=FSMAdmin.main)
    dp.register_callback_query_handler(sales_redactor, text='admin_back_to_sales', state=FSMAdmin.main)
    dp.register_callback_query_handler(sales_caption_redactor, text='admin_sales_change_desc', state=FSMAdmin.main)
    dp.register_callback_query_handler(sales_switch, text='admin_sales_switch_sale', state=FSMAdmin.main)
    dp.register_callback_query_handler(sales_photo_redactor, text='admin_sales_change_photo', state=FSMAdmin.main)
    with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
        all_sales_json = f.read()
    all_sales = json.loads(all_sales_json)
    for i in range(1, len(all_sales["context"]) + 1):
        dp.register_message_handler(sales_photo_confirm, content_types=['photo'], state=FSMAdmin.salephoto[i])
        dp.register_callback_query_handler(sales_back_to_pages_desc, text='sales_list_back', state=FSMAdmin.sale[i])
        dp.register_callback_query_handler(sales_back_to_pages_photo, text='sales_list_back', state=FSMAdmin.salephoto[i])
    dp.register_callback_query_handler(sales_add, text='admin_sales_add_sale', state=FSMAdmin.main)
    dp.register_message_handler(sales_add_photo, content_types=['photo'], state=FSMAdmin.newsale_photo)
    dp.register_callback_query_handler(sales_redactor, text='sales_list_back', state=FSMAdmin.newsale_description)
    dp.register_callback_query_handler(sales_add, text='sales_list_back', state=FSMAdmin.newsale_photo)
    dp.register_callback_query_handler(sales_add_photo_confirm, text='sales_add_confirm', state=FSMAdmin.sale_add)
    dp.register_callback_query_handler(sales_add, text='sales_add_cancel', state=FSMAdmin.sale_add)
    dp.register_callback_query_handler(admin_enter, text='users_db_back', state=FSMAdmin.main)
    dp.register_callback_query_handler(moysklad_users_db, text='users_moysklad', state=FSMAdmin.main)
    dp.register_callback_query_handler(bot_db_output, text='users_bot', state=FSMAdmin.main)
    dp.register_callback_query_handler(users_db_back, text='users_db_in_back', state=FSMAdmin.main)
