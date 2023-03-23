async def format_time(time: int):
    """Функция для правильного склонения времени.
    Работает с секундами, минутами, часами и днями.
    """
    two_to_four = ("2", "3", "4")
    five_to_zero = ("5", "6", "7", "8", "9", "0")
    eleven_to_fourteen = ("11", "12", "13", "14")
    to_return = f'Следующая загрузка базы данных будет через: '
    if time <= 0:
        return 0
    if time > 216000:
        return to_return + await days_hours_minutes_seconds(time, two_to_four, five_to_zero, eleven_to_fourteen)
    if time > 3600:
        return to_return + await hours_minutes_seconds(time, two_to_four, five_to_zero, eleven_to_fourteen)
    if time > 60:
        return to_return + await minutes_seconds(time, two_to_four, five_to_zero, eleven_to_fourteen)
    return to_return + await seconds(time, two_to_four, five_to_zero, eleven_to_fourteen)


async def seconds(time: int, two_to_four: tuple, five_to_zero: tuple, eleven_to_fourteen: tuple):
    time_str = str(time)
    if time_str == '0':
        return ''
    if time_str.endswith(eleven_to_fourteen):
        return f'{time_str} секунд'
    if time_str.endswith('1'):
        return f'{time_str} секунду'
    if time_str.endswith(two_to_four):
        return f'{time_str} секунды'
    if time_str.endswith(five_to_zero):
        return f'{time_str} секунд'
    raise ValueError(f'Количество секунд неверное: {time_str}')


async def minutes_seconds(time: int, two_to_four: tuple, five_to_zero: tuple, eleven_to_fourteen: tuple):
    time_str_min = str(time // 60)
    time_sec = time - int(time_str_min) * 60
    if time_str_min.endswith(eleven_to_fourteen):
        return f'{time_str_min} минут {await seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_min.endswith('1'):
        return f'{time_str_min} минуту {await seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_min.endswith(two_to_four):
        return f'{time_str_min} минуты {await seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_min.endswith(five_to_zero):
        return f'{time_str_min} минут {await seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    raise ValueError(f'Количество минут неверное: {time_str_min}')


async def hours_minutes_seconds(time: int, two_to_four: tuple, five_to_zero: tuple, eleven_to_fourteen: tuple):
    time_str_hours = str(time // 3600)
    time_sec = time - int(time_str_hours) * 3600
    if time_str_hours.endswith(eleven_to_fourteen):
        return f'{time_str_hours} часов ' \
               f'{await minutes_seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_hours.endswith('1'):
        return f'{time_str_hours} час {await minutes_seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_hours.endswith(two_to_four):
        return f'{time_str_hours} часа {await minutes_seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_hours.endswith(five_to_zero):
        return f'{time_str_hours} часов ' \
               f'{await minutes_seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    raise ValueError(f'Количество часов неверное: {time_str_hours}')


async def days_hours_minutes_seconds(time: int, two_to_four: tuple, five_to_zero: tuple, eleven_to_fourteen: tuple):
    time_str_days = str(time // 216000)
    time_sec = time - int(time_str_days) * 216000
    if time_str_days.endswith(eleven_to_fourteen):
        return f'{time_str_days} дней ' \
               f'{await hours_minutes_seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_days.endswith('1'):
        return f'{time_str_days} день ' \
               f'{await hours_minutes_seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_days.endswith(two_to_four):
        return f'{time_str_days} дня ' \
               f'{await hours_minutes_seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    if time_str_days.endswith(five_to_zero):
        return f'{time_str_days} дней ' \
               f'{await hours_minutes_seconds(time_sec, two_to_four, five_to_zero, eleven_to_fourteen)}'
    raise ValueError(f'Количество дней неверное: {time_str_days}')
