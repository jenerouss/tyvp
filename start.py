import asyncio
import configparser
import json
import logging.config
import multiprocessing
import os
import sqlite3
from ctypes import c_long
from time import sleep

from aiogram.utils import executor

from create_bot import dp
from data_base import sqlite_db
from handlers import admin, client
from loadbase import loadbasemain

logging.config.fileConfig('config/logs/logsettings.conf', disable_existing_loggers=False)


class OnStartUp:
    def __init__(self):
        self.bot_process: multiprocessing.Process | None = None
        self.update_process: multiprocessing.Process | None = None
        self.restart_event = multiprocessing.Event()
        self.shutdown_event = multiprocessing.Value(c_long)
        self.sleep_time = multiprocessing.Value(c_long)
        self.slept_time = multiprocessing.Value(c_long)
        self.restart_id = multiprocessing.Value(c_long)

    def run(self):
        """1 - выключение всего ; 0 - рестарт всего ; 2 - рестарт обновления бд
        """
        self.start_bot()
        self.start_update_base()
        while self.restart_event.wait():
            self.restart_event.clear()
            if self.shutdown_event.value == 1:
                self.stop_all()
            if self.shutdown_event.value == 0:
                self.stop_all()
                self.start_bot(restart=self.restart_id.value)
                self.start_update_base()
            if self.shutdown_event.value == 2:
                self.stop_update_base()
                self.start_update_base()

    def stop_all(self):
        """Завершение процесса бота и обновления базы данных
        """
        if self.bot_process is not None:
            self.bot_process.kill()
            self.bot_process = None
        if self.update_process is not None:
            self.update_process.kill()
            self.update_process = None

    def stop_update_base(self):
        """Завершение процесса обновления базы данных
        """
        if self.update_process is not None:
            self.update_process.kill()
            self.update_process = None

    def start_bot(self, **kwargs):
        """Запуск бота, при перезапуске бота можно передать
         параметр restart со значением id пользователя телеграмм,
         которому отправиться сообщение о том, что бот перезапущен.
         """
        if 'restart' in kwargs:
            asyncio.run(dp.bot.send_message(chat_id=kwargs['restart'], text='Бот перезапущен'))
        if self.bot_process is not None:
            raise RuntimeError('процесс запустился второй раз')
        self.bot_process = multiprocessing.Process(target=bot_process, args=(self.restart_event, self.shutdown_event,
                                                                             self.sleep_time, self.slept_time,
                                                                             self.restart_id,))
        self.bot_process.start()

    def start_update_base(self):
        """Запуск процесса обновления базы данных
        """
        if self.update_process is not None:
            raise RuntimeError('процесс запустился второй раз')
        if not os.path.exists('config/мойсклад'):
            os.mkdir('config/мойсклад')
        self.update_process = multiprocessing.Process(target=update_process, args=(self.sleep_time, self.slept_time,))
        self.update_process.start()


async def on_startup(_):
    """Запуск Sql при старте бота
    """
    await sqlite_db.sql_start()


def bot_process(restart_event, shutdown_event, sleep_time, slept_time, restart_id):
    """Процесс бота.
    sleep_time и slept_time нужны для отображения в
    клиентской части бота время последнего
    и следующего обновления базы данных
    :param restart_event: нужен для перезапуска бота
    :param shutdown_event: для выключения бота
    :param sleep_time: сколько нужно спать
    :param slept_time: сколько процесс спал
    :param restart_id: id пользователя в телеграмм
    которому отправится сообщение в случае перезапуска бота.
    """
    dp.storage.data['__restart_event'] = restart_event
    dp.storage.data['__shutdown_event'] = shutdown_event
    dp.storage.data['__restart_id'] = restart_id
    dp.storage.data['__sleep_time'] = sleep_time
    dp.storage.data['__slept_time'] = slept_time
    client.register_handlers_client(dp)
    admin.register_handlers_admin(dp)
    with open('config/клавиатуры и типы/buttons.json', 'r', encoding='utf-8') as f:
        current_buttons = f.read()
    with open('config/клавиатуры и типы/buttons_backup.json', 'w', encoding='utf-8') as file:
        file.write(current_buttons)
    while True:
        try:
            executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
        except Exception as e:
            print(e)
            sleep(1)


def update_process(sleep_time, slept_time):
    """Процесс обновления базы данных
    """
    config = configparser.ConfigParser()
    config.read('config/settings.ini')
    sleep_time.value = int(config['DB']['data_base_load_timer_seconds'])
    while True:
        slept_time.value = 0
        while slept_time.value < sleep_time.value:
            sleep(1)
            slept_time.value += 1
        logging.info("slept time %s seconds", slept_time.value)
        asyncio.run(loadbasemain.load(force_load=False))


def fix_buttons():
    """config -> клавиатуры и типы -> buttons.json удаление кнопок, если их названий нет с базе данных
    """
    with open('config/клавиатуры и типы/buttons.json', 'r', encoding='utf-8') as file:
        buttons_json = file.read()
    buttons = json.loads(buttons_json)
    buttons_fixed = buttons.copy()
    for i in buttons:
        for j in buttons[i]:
            try:
                search = asyncio.run(sqlite_db.data_from_sql('goods', 'name', j))
            except sqlite3.OperationalError:
                print('Ошибка при удалении кнопок, вероятнее всего это связно с тем, что в бд еще не загружены товары '
                      'с мойсклад. Запускаю принудительную загрузку бд мойсклад. Если ошибка повторится, просьба '
                      'обратиться к кодеру.')
                asyncio.run(sqlite_db.sql_start())
                return 1
            if len(search) == 0:
                print('Удаляю кнопку, названия которой нет в базе данных: ', search, len(search), j)
                buttons_fixed[i].remove(j)
    with open('config/клавиатуры и типы/buttons.json', 'w', encoding='utf-8') as file:
        json.dump(buttons_fixed, file, indent=4, ensure_ascii=False)


def file_work():
    """Добавление конфигурационных файлов
    со стандартными значениями в случае их
    отсутствия
    """
    if not os.path.exists('bot_run.bat'):
        print('Создаю файл bot_run.bat')
        with open('bot_run.bat', 'w+') as f:
            f.write('@echo off\n\ncall %~dp0venv\Scripts\\activate\n\npython start.py\n\npause')
    if not os.path.exists('readme.txt'):
        print('Создаю файл readme.txt')
        with open('readme.txt', 'w+') as f:
            f.write('Если при запуске в консоль пишет что то вроде\n\nTraceback (most recent call last):\n\tFile'
                    ' "C:\\Users\\Jenerous\\PycharmProjects\\tyvporyadke\\start.py", line 12, in <module>\n\t\t'
                    "from aiogram.utils import executor\nModuleNotFoundError: No module named 'aiogram'\n\n"
                    "то нужно открыть консоль в этой папке и прописать pip install -r requirements.txt\n\n"
                    "по пути config -> settings.ini нужно вписать логин и пароль от аккаунта мойсклад,\n"
                    "во вторую и третью переменную соответственно. писать после равно, никаких пробелов\n"
                    "или переносов на новую строку в конце быть не должно, иначе бот не сможет обновлять\n"
                    "бд мойсклад, в таком случае в консоль будет выводиться что-то вроде 'rows'\n\n"
                    "остальные файлы изменять, удалять, перемещать нельзя, иначе бот будет работать некорректно, "
                    "либо вовсе не запустится")
    if not os.path.exists('requirements.txt'):
        print('Создаю файл requirements.txt')
        with open('requirements.txt', 'w+') as f:
            f.write('aiogram~=2.23.1\nrequests~=2.28.2')


if __name__ == '__main__':
    file_work()
    if fix_buttons() == 1:
        asyncio.run(loadbasemain.load(force_load=True))
        fix_buttons()
    OnStartUp().run()

# Todo: сделать статистику в sql
# Todo: если все акции неактивны, кнопка из главного меню пропадает
