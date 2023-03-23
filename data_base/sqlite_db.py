import datetime
import sqlite3 as sq

from aiogram.dispatcher import FSMContext

base = sq.connect('database.db')
cur = base.cursor()


async def sql_start():
    """Подключение либо создание бд пользователей
    """
    cur.execute('CREATE TABLE IF NOT EXISTS botusers(id INTEGER PRIMARY KEY, name TEXT, number TEXT, username TEXT,'
                ' status TEXT, activity INTEGER, last_activity TEXT, registration_date TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS goods(name TEXT PRIMARY KEY, pathName TEXT, price INTEGER, stock INTEGER)')
    cur.execute('CREATE TABLE IF NOT EXISTS bonususers(number TEXT, name TEXT, salesAmount INTEGER,'
                'bonusPoints INTEGER)')
    base.commit()


async def sql_add_command(table: str, data: dict):
    """Добавить строку со всеми полями
    """
    cur.execute(f'INSERT INTO {table} VALUES(?, ?, ?, ?, ?, ?, ?, ?)', tuple(data.values()))
    base.commit()


async def sql_update_command(table: str, data: dict, what: str, user_id: int):
    """Установить значение what, пользователю с айди user_id
    """
    cur.execute(f'UPDATE {table} SET {what} == ? WHERE id == ?', ((data[f'{what}']), user_id))
    base.commit()


async def check_user_reg(table: str, user_id: int):
    """Проверить user_id на наличие в бд
    """
    try:
        cur.execute(f'SELECT id FROM {table} WHERE id == {user_id}')
        data = cur.fetchone()
    except Exception as e:
        print(e)
        return 0
    if data is None:
        return 0
    else:
        return 1


async def count_users(table: str, state: FSMContext):
    """Посчитать все поля
    """
    async with state.proxy() as data:
        cur.execute(f'SELECT id FROM {table}')
        data = cur.fetchall()
        if data is None:
            return 0
        else:
            return len(data)


# Todo:
async def return_all(table: str, state: FSMContext, amount: int):
    """Вернуть все поля и их значения
    """
    response = ''
    async with state.proxy() as data:
        for i in range(amount):
            try:
                cur.execute(f'SELECT * FROM {table}')
                data = cur.fetchall()
                response += f'{i + 1}) Айди: {str(data[i][0])}\n Имя: {str(data[i][1])}\n Телефон: ' \
                            f'{str(data[i][2])}\n Имя в телеграмме: {str(data[i][3])}\n Роль: ' \
                            f'{str(data[i][4])}\n Кол-во отправленных сообщений: ' \
                            f'{str(data[i][5])}\n Дата регистрации: {str(data[i][6])}\n\n'
            except Exception as e:
                print(e)
        if data is None:
            return 0
        else:
            return response


async def check_user_rank(table: str, state: FSMContext, user_id: int):
    """Вернуть ранг user_id
    """
    async with state.proxy() as data:
        cur.execute(f'SELECT status FROM {table} WHERE id == {user_id}')
        data = cur.fetchall()
        if data is None:
            return 0
        else:
            return data[0][0]


async def check_user_number(table: str, state: FSMContext, user_id: int):
    """Вернуть номер телефона user_id
    """
    async with state.proxy() as data:
        cur.execute(f'SELECT number FROM {table} WHERE id == {user_id}')
        data = cur.fetchall()
        if data is None:
            return 0
        else:
            return data[0][0]


async def msg_update(table: str, user_id: int):
    """Обновить значение поля activity для user_id
    """
    if not await check_user_reg(table, user_id):
        return 0
    try:
        cur.execute(f'SELECT activity FROM {table} WHERE id == {user_id}')
        data = cur.fetchall()
    except Exception as e:
        print(e)
        return 0
    if len(data) == 0:
        ms = 1
    else:
        ms = int(data[0][0]) + 1
    cur.execute(f'UPDATE {table} SET activity == ? WHERE id == ?', (ms, user_id))
    base.commit()
    await activity_update(table, user_id)
    return 1


async def activity_update(table: str, user_id: int):
    """Обновить значение поля last_activity пользователю user_id
    """
    if not await check_user_reg(table, user_id):
        return 0
    timee = str(datetime.datetime.today().strftime('%H:%M:%S %Y-%m-%d'))
    cur.execute(f'UPDATE {table} SET last_activity == ? WHERE id == ?',
                (timee, user_id))
    base.commit()
    return 1


async def user_name_update(table: str, name: str, user_id: int):
    """Обновить username для user_id
    """
    cur.execute(f'UPDATE {table} SET username == ? WHERE id == ?', (name, user_id))
    base.commit()


async def convert_json_to_sql(table: str, data: list, add: bool):
    """add: нужен для добавления данных в таблицу:
    True - таблица перезаписывается;
    False - сортируется и дополняется
    """
    if add:
        for i in range(len(data)):
            try:
                cur.execute(f'INSERT INTO {table} VALUES(?, ?, ?, ?)', tuple(data[i].values()))
            except sq.IntegrityError:
                pass
        all_data = await data_from_sql(table, column='name', value=' ')
        all_data.sort(key=lambda x: x[0])
        cur.execute(f'DELETE FROM {table}')
        for i in range(len(all_data)):
            try:
                cur.execute(f'INSERT INTO {table} VALUES(?, ?, ?, ?)', all_data[i])
            except sq.IntegrityError:
                pass
    else:
        cur.execute(f'DELETE FROM {table}')
        for i in range(len(data)):
            try:
                cur.execute(f'INSERT INTO {table} VALUES(?, ?, ?, ?)', tuple(data[i].values()))
            except sq.IntegrityError:
                pass
    base.commit()


async def data_from_sql(table: str, column: str, value: str, **kwargs):
    """Ищет данные value с sql таблицы.
    table - название таблицы. column - название столбца.
    Если нужно проводить поиск в таблице по номеру телефона,
    нужно передать параметр phone_format с любым значением.
    """
    if 'phone_format' in kwargs:
        cur.execute(f"SELECT * FROM {table} WHERE {column} LIKE ?", (f"%{value}%", ))
        return cur.fetchall()
    cur.execute(f"SELECT * FROM {table} WHERE {column} LIKE ?", (f"%{value.upper()}%", ))
    return cur.fetchall()
