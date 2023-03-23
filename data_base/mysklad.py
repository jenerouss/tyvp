import json

from create_bot import bot
from data_base import sqlite_db


async def data_base(state):
    """Дата последнего изменения бд
    """
    sleep_time = state.storage.data['__sleep_time'].value
    slept_time = state.storage.data['__slept_time'].value
    return sleep_time - slept_time


async def bonus_search(number):
    """Поиск человека в бонуске
    """
    user = await sqlite_db.data_from_sql('bonususers', 'number', number, phone_format=True)
    if len(user) < 1:
        return None
    if len(user) > 1:
        await bot.send_message(chat_id=501209907, text=(str('На один номер телефона существует два человека:' + number +
                                                        user)))
    name = str(user[0][1])
    bonus_points = str(user[0][3]) + ' баллов'
    all_types = f'{name}\n{number}\n{bonus_points}'
    return all_types


async def search_type(typo):
    """Поиск в ассортименте по типу
    """
    all_products = await sqlite_db.data_from_sql('goods', 'pathName', typo)
    all_types = []
    for i in range(len(all_products)):
        price = str(all_products[i][2])
        stock = str(all_products[i][3])
        if stock == 'NaN':
            all_types.append(f'{str(all_products[i][0])} - {price} руб.')
        else:
            all_types.append(f'{str(all_products[i][0])} - {price} руб. - {stock} шт.')
    if len(all_types) == 0:
        return 0
    all_types.sort()
    return all_types


async def search_type_nottype(typo, nottypo):
    """Поиск в ассортименте по типу и нетипу. нетип не должен входить в тип
    """
    all_products = await sqlite_db.data_from_sql('goods', 'pathName', typo)
    all_types = []
    for i in range(len(all_products)):
        if nottypo in all_products[i][1]:
            continue
        price = str(all_products[i][2])
        stock = str(all_products[i][3])
        if stock == 'NaN':
            all_types.append(f'{str(all_products[i][0])} - {price} руб.')
        else:
            all_types.append(f'{str(all_products[i][0])} - {price} руб. - {stock} шт.')
    if len(all_types) == 0:
        return 0
    all_types.sort()
    return all_types


async def search_name_type_inline(name, typo, offset):
    """Поиск по имени и типу, сплит для inline режима
    """
    all_products = await sqlite_db.data_from_sql('goods', 'name', name)
    all_types = []
    typo = str(typo)
    if typo == '0':
        for i in range(len(all_products)):
            if name.lower() in all_products[i][0].lower():
                price = str(all_products[i][2])
                stock = str(all_products[i][3])
                if stock == 'NaN':
                    all_types.append(f'{str(all_products[i][0])}^{price} руб.')
                else:
                    all_types.append(f'{str(all_products[i][0])}^{price} руб.^{stock} шт.')
    else:
        for i in range(len(all_products)):
            if name.lower() in all_products[i][0].lower() and typo.lower() in all_products[i][1].lower():
                price = str(all_products[i][2])
                stock = str(all_products[i][3])
                if stock == 'NaN':
                    all_types.append(f'{str(all_products[i][0])}^{price} руб.')
                else:
                    all_types.append(f'{str(all_products[i][0])}^{price} руб.^{stock} шт.')
    overall_items = len(all_types)
    all_types.sort()
    if offset >= overall_items:
        return []
    elif offset + 50 >= overall_items:
        return all_types[offset:overall_items + 1]
    else:
        return all_types[offset:offset + 50]


async def search_name_type(name, typo):
    """Поиск по имени и типу
    """
    all_products = await sqlite_db.data_from_sql('goods', 'name', name)
    all_types = []
    for i in range(len(all_products)):
        if typo not in all_products[i][1]:
            continue
        price = str(all_products[i][2])
        stock = str(all_products[i][3])
        if stock == 'NaN':
            all_types.append(f'{str(all_products[i][0])} - {price} руб.')
        else:
            all_types.append(f'{str(all_products[i][0])} - {price} руб. - {stock} шт.')
    if len(all_types) == 0:
        return 0
    all_types.sort()
    return all_types


async def search_name_type_nottype(name, typo, nottypo):
    """Поиск по имени, типу и nottype - то, что не должно быть в типе(РАСХОДНИКИ УСТРОЙСТВА: если нужны только
     расходники, type=РАСХОДНИКИ, nottype=УСТРОЙСТВА)
     """
    all_products = await sqlite_db.data_from_sql('goods', 'name', name)
    all_types = []
    for i in range(len(all_products)):
        if nottypo in all_products[i][1]:
            continue
        if typo not in all_products[i][1]:
            continue
        price = str(all_products[i][2])
        stock = str(all_products[i][3])
        if stock == 'NaN':
            all_types.append(f'{str(all_products[i][0])} - {price} руб.')
        else:
            all_types.append(f'{str(all_products[i][0])} - {price} руб. - {stock} шт.')
    if len(all_types) == 0:
        return 0
    all_types.sort()
    return all_types


async def hookah_complect():
    """Комлектующие для кальяна
    """
    all_products = await sqlite_db.data_from_sql('goods', 'pathName', 'КОМПЛЕКТУЮЩИЕ КАЛЬЯН')
    all_types = []
    for i in range(len(all_products)):
        price = str(all_products[i][2])
        stock = str(all_products[i][3])
        if stock == 'NaN':
            all_types.append(f'{str(all_products[i][0])} - {price} руб.')
        else:
            all_types.append(f'{str(all_products[i][0])} - {price} руб. - {stock} шт.')
    if len(all_types) == 0:
        return 0
    all_types.sort()
    return all_types


async def vape_search_inline(name, offset):
    """Поиск по вейп продукции для inline режима
    """
    all_products = await sqlite_db.data_from_sql('goods', 'name', name)
    with open("config/клавиатуры и типы/hookahandvapetypes.json", 'r', encoding='utf-8') as f:
        all_types_json = f.read()
    all_types = json.loads(all_types_json)
    all_output = []
    for i in range(len(all_products)):
        for j in range(len(all_types['вейп'])):
            if all_types['вейп'][j].lower() in all_products[i][1].lower():
                price = str(all_products[i][2])
                stock = str(all_products[i][3])
                if stock == 'NaN':
                    all_output.append(f'{str(all_products[i][0])}^{price} руб.')
                else:
                    all_output.append(f'{str(all_products[i][0])}^{price} руб.^{stock} шт.')
    overall_items = len(all_output)
    all_output.sort()
    if offset >= overall_items:
        return []
    elif offset + 50 >= overall_items:
        return all_output[offset:overall_items + 1]
    else:
        return all_output[offset:offset + 50]


async def hookah_search_inline(name, offset):
    """Поиск по кальянной продукции для inline режима
    """
    all_products = await sqlite_db.data_from_sql('goods', 'name', name)
    with open("config/клавиатуры и типы/hookahandvapetypes.json", 'r', encoding='utf-8') as f:
        all_types_json = f.read()
    all_types = json.loads(all_types_json)
    all_output = []
    for i in range(len(all_products)):
        for j in range(len(all_types['кальян'])):
            if all_types['кальян'][j].lower() in all_products[i][1].lower():
                price = str(all_products[i][2])
                stock = str(all_products[i][3])
                if stock == 'NaN':
                    all_output.append(f'{str(all_products[i][0])}^{price} руб.')
                else:
                    all_output.append(f'{str(all_products[i][0])}^{price} руб.^{stock} шт.')
    overall_items = len(all_output)
    all_output.sort()
    if offset >= overall_items:
        return []
    elif offset + 50 >= overall_items:
        return all_output[offset:overall_items + 1]
    else:
        return all_output[offset:offset + 50]
