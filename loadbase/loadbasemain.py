import configparser
import json
from datetime import datetime
from time import sleep

import requests

from data_base import sqlite_db


async def load(force_load: bool):
    """Функция загрузки базы данных с Мойсклад,
    :param force_load: True в случае принудительной загрузки.
    """
    if force_load:
        print("Запускаю принудительную загрузку базу данных МойСклад:\n")
    else:
        print("Запускаю плановую загрузку базы данных МойСклад:\n")
    try:
        print("Загружаю ассортимент товаров:\n")
        link = "https://online.moysklad.ru/api/remap/1.2/entity/assortment"
        data = await get_data(link)
        await json_to_sql("assortment", data, add=False)
        size = data["meta"]["size"]
        offset = 1000
        while size > 1000:
            link = f"https://online.moysklad.ru/api/remap/1.2/entity/assortment?offset={offset}"
            data = await get_data(link)
            offset += 1000
            size -= 1000
            await json_to_sql("assortment", data, add=True)
        print("Загружаю пользователей из бонусной программы:\n")
        link = "https://online.moysklad.ru/api/remap/1.2/entity/counterparty"
        data = await get_data(link)
        await json_to_sql("bonus", data, add=False)
        size = data["meta"]["size"]
        offset = 1000
        while size > 1000:
            link = f"https://online.moysklad.ru/api/remap/1.2/entity/counterparty?offset={offset}"
            data = await get_data(link)
            offset += 1000
            size -= 1000
            await json_to_sql("bonus", data, add=True)
    except Exception as e:
        print(e)
    print('База данных МойСклад загружена.')
    with open('config/мойсклад/last_load.txt', 'w') as file:
        file.write(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


async def get_data(link: str):
    """Этап проверки на корректность json формата
    """
    response = await request_load(link)
    flag = True
    while flag:
        try:
            data = response.json()
        except Exception as e:
            print(e, ', загружаю еще раз')
            data = response.json()
        else:
            flag = False
    return data


async def request_load(link: str):
    """Этап загрузки данных
    """
    try:
        config = configparser.ConfigParser()
        config.read('config/settings.ini')
        user_name = config['DB']['data_base_user_name']
        user_password = config['DB']['data_base_user_password']
    except Exception as e:
        print(e)
        return
    while True:
        try:
            response = requests.get(url=link, auth=(user_name, user_password), stream=True)
        except Exception as e:
            print(e)
            sleep(5)
        else:
            return response


async def json_to_sql(prefix: str, json_input: json, add: bool):
    """Перевод json данных в sql
    :param prefix: assortment либо bonus
    :param json_input: переносится в sql
    :param add: нужен для добавления данных в таблицу:
    True - таблица перезаписывается;
    False - сортируется и дополняется
    """
    data = []
    if prefix.startswith('assortment'):
        for count, value in enumerate(json_input["rows"]):
            x = int(value.get('stock', 0))
            if x < 1 and 'УСЛУГИ' in value.get('pathName').upper():
                data_to_add = {
                    'name': str(value.get('name', 'Наименование отсутствует') + ' ').upper(),
                    'pathName': value.get('pathName', 'Путь отсутствует').upper(),
                    'price': int(value.get('salePrices')[0]['value'] / 100),
                    'stock': 'NaN'
                }
                data.append(data_to_add)
                continue
            elif x < 1:
                continue
            data_to_add = {
                'name': str(value.get('name', 'Наименование отсутствует') + ' ').upper(),
                'pathName': value.get('pathName', 'Путь отсутствует').upper(),
                'price': int(value.get('salePrices')[0]['value'] / 100),
                'stock': x
            }
            data.append(data_to_add)
        data.sort(key=lambda s: s["name"])
        await sqlite_db.convert_json_to_sql('goods', data, add)
    elif prefix.startswith('bonus'):
        for count, value in enumerate(json_input["rows"]):
            try:
                sa = int(value.get('salesAmount')) / 100
            except TypeError:
                sa = value.get('salesAmount')
            try:
                bp = int(value.get('bonusPoints'))
            except TypeError:
                bp = value.get('bonusPoints')
            data_to_add = {
                'number': value.get('phone', 'Номер телефона отсутствует'),
                'name': value.get('name', 'ФИО отсутствует'),
                'salesAmount': sa,
                'bonusPoints': bp
            }
            data.append(data_to_add)
        data.sort(key=lambda s: s["name"])
        await sqlite_db.convert_json_to_sql('bonususers', data, add)
