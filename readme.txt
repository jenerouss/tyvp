Если при запуске в консоль пишет что то вроде

Traceback (most recent call last):
	File "C:\Users\Jenerous\PycharmProjects\tyvporyadke\start.py", line 12, in <module>
		from aiogram.utils import executor
ModuleNotFoundError: No module named 'aiogram'

то нужно открыть консоль в этой папке и прописать pip install -r requirements.txt

по пути config -> settings.ini нужно вписать логин и пароль от аккаунта мойсклад,
во вторую и третью переменную соответственно. писать после равно, никаких пробелов
или переносов на новую строку в конце быть не должно, иначе бот не сможет обновлять
бд мойсклад, в таком случае в консоль будет выводиться что-то вроде 'rows'

остальные файлы изменять, удалять, перемещать нельзя, иначе бот будет работать некорректно, либо вовсе не запустится