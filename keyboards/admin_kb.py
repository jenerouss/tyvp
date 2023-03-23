import json

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

kb_admin_main = ReplyKeyboardMarkup(row_width=2)
button0_admin_main = KeyboardButton(text='Выйти из админ панели')
button1_admin_main = KeyboardButton(text='Редактор клавиатур')
button2_admin_main = KeyboardButton(text='Редактор акций')
button3_admin_main = KeyboardButton(text='Бд пользователей')
button5_admin_main = KeyboardButton(text='Статистика')
button6_admin_main = KeyboardButton(text='Действия с ботом')
kb_admin_main.add(button0_admin_main).add(button1_admin_main).add(button2_admin_main).add(button3_admin_main) \
    .add(button5_admin_main).add(button6_admin_main)

kb_admin_kb_redactor = InlineKeyboardMarkup(row_width=2)
button1_kb_redactor = InlineKeyboardButton(text='Кнопки клавиатур', callback_data='kb_buttons')
button2_kb_redactor = InlineKeyboardButton(text='Типы для поиска', callback_data='search_types')
button3_kb_redactor = InlineKeyboardButton(text='Вернуться назад', callback_data='path_choose_back')
kb_admin_kb_redactor.add(button1_kb_redactor).add(button2_kb_redactor).add(button3_kb_redactor)

kb_admin_redactor_kb_path_choose = InlineKeyboardMarkup(row_width=2)
button1_redactor_kb_path_choose = InlineKeyboardButton(text='Добавить кнопку', callback_data='add_button')
button2_redactor_kb_path_choose = InlineKeyboardButton(text='Удалить кнопку', callback_data='delete_button')
button3_redactor_kb_path_choose = InlineKeyboardButton(text='Вернуться назад', callback_data='search_types_back')
kb_admin_redactor_kb_path_choose.add(button1_redactor_kb_path_choose).add(button2_redactor_kb_path_choose).add(
    button3_redactor_kb_path_choose)

kb_admin_redactor_kb_path_choose_add = InlineKeyboardMarkup(row_width=2)
button1_redactor_kb_path_choose_add = InlineKeyboardButton(text='Табак', callback_data='add_button_tabak')
button2_redactor_kb_path_choose_add = InlineKeyboardButton(text='Жидкости', callback_data='add_button_zizi')
button3_redactor_kb_path_choose_add = InlineKeyboardButton(text='Одноразки', callback_data='add_button_odnorazki')
button4_redactor_kb_path_choose_add = InlineKeyboardButton(text='Устройства', callback_data='add_button_devices')
button5_redactor_kb_path_choose_add = InlineKeyboardButton(text='Расходники', callback_data='add_button_cartriges')
button6_redactor_kb_path_choose_add = InlineKeyboardButton(text='Вернуться назад',
                                                           callback_data='kb_redactor_types_back')
kb_admin_redactor_kb_path_choose_add.add(button1_redactor_kb_path_choose_add).add(button2_redactor_kb_path_choose_add)\
    .add(button3_redactor_kb_path_choose_add).add(button4_redactor_kb_path_choose_add)\
    .add(button5_redactor_kb_path_choose_add).add(button6_redactor_kb_path_choose_add)

kb_admin_redactor_kb_path_choose_delete = InlineKeyboardMarkup(row_width=2)
button1_redactor_kb_path_choose_delete = InlineKeyboardButton(text='Табак', callback_data='delete_button_tabak')
button2_redactor_kb_path_choose_delete = InlineKeyboardButton(text='Жидкости', callback_data='delete_button_zizi')
button3_redactor_kb_path_choose_delete = InlineKeyboardButton(text='Одноразки', callback_data='delete_button_odnorazki')
button4_redactor_kb_path_choose_delete = InlineKeyboardButton(text='Устройства', callback_data='delete_button_devices')
button5_redactor_kb_path_choose_delete = InlineKeyboardButton(text='Расходники',
                                                              callback_data='delete_button_cartriges')
button6_redactor_kb_path_choose_delete = InlineKeyboardButton(text='Вернуться назад',
                                                              callback_data='kb_redactor_types_back')
kb_admin_redactor_kb_path_choose_delete.add(button1_redactor_kb_path_choose_delete).add(
    button2_redactor_kb_path_choose_delete).add(button3_redactor_kb_path_choose_delete)\
    .add(button4_redactor_kb_path_choose_delete).add(button5_redactor_kb_path_choose_delete)\
    .add(button6_redactor_kb_path_choose_delete)

kb_admin_redactor_kb_add_path_choose_back = InlineKeyboardMarkup(row_width=2)
button1_redactor_kb_add_path_choose_back = InlineKeyboardButton(text='Назад',
                                                                callback_data='redactor_kb_add_path_choose_back')
kb_admin_redactor_kb_add_path_choose_back.add(button1_redactor_kb_add_path_choose_back)

kb_admin_redactor_kb_path_delete_choose_back = InlineKeyboardMarkup(row_width=2)
button1_redactor_kb_path_delete_choose_back = InlineKeyboardButton(text='Назад',
                                                                   callback_data='redactor_kb_path_delete_choose_back')
kb_admin_redactor_kb_path_delete_choose_back.add(button1_redactor_kb_path_delete_choose_back)

kb_admin_redactor_types_path_choose = InlineKeyboardMarkup(row_width=2)
button1_redactor_types_path_choose = InlineKeyboardButton(text='Добавить тип', callback_data='add_type')
button2_redactor_types_path_choose = InlineKeyboardButton(text='Удалить тип', callback_data='delete_type')
button3_redactor_types_path_choose = InlineKeyboardButton(text='Вернуться назад', callback_data='search_types_back')
kb_admin_redactor_types_path_choose.add(button1_redactor_types_path_choose).add(button2_redactor_types_path_choose).add(
    button3_redactor_types_path_choose)

kb_admin_redactor_types_choose_add = InlineKeyboardMarkup(row_width=2)
button1_redactor_types_choose_add = InlineKeyboardButton(text='Кальян', callback_data='hookah_add')
button2_redactor_types_choose_add = InlineKeyboardButton(text='Вейп', callback_data='vape_add')
button3_redactor_types_choose_add = InlineKeyboardButton(text='Вернуться назад', callback_data='search_types_add_back')
kb_admin_redactor_types_choose_add.add(button1_redactor_types_choose_add).add(button2_redactor_types_choose_add).add(
    button3_redactor_types_choose_add)

kb_admin_redactor_types_choose_delete = InlineKeyboardMarkup(row_width=2)
button1_redactor_types_choose_delete = InlineKeyboardButton(text='Кальян', callback_data='hookah_delete')
button2_redactor_types_choose_delete = InlineKeyboardButton(text='Вейп', callback_data='vape_delete')
button3_redactor_types_choose_delete = InlineKeyboardButton(text='Вернуться назад',
                                                            callback_data='search_types_add_back')
kb_admin_redactor_types_choose_delete.add(button1_redactor_types_choose_delete).add(
    button2_redactor_types_choose_delete).add(button3_redactor_types_choose_delete)

kb_admin_redactor_types_choose_back = InlineKeyboardMarkup(row_width=2)
button1_redactor_types_choose_back = InlineKeyboardButton(text='Назад', callback_data='search_types_add_choose_back')
kb_admin_redactor_types_choose_back.add(button1_redactor_types_choose_back)

kb_admin_bot_actions = InlineKeyboardMarkup(row_width=2)
button1_bot_actions = InlineKeyboardButton(text='🔄Перезапуск бота', callback_data='restart_bot')
button2_bot_actions = InlineKeyboardButton(text='🚫Выключить бота', callback_data='shutdown_bot')
button3_bot_actions = InlineKeyboardButton(text='🗂МойСклад', callback_data='moysklad')
button4_bot_actions = InlineKeyboardButton(text='Назад', callback_data='bot_actions_back')
kb_admin_bot_actions.add(button1_bot_actions).add(button2_bot_actions).add(button3_bot_actions).add(button4_bot_actions)

kb_admin_shutdown = InlineKeyboardMarkup(row_width=2)
button1_shutdown = InlineKeyboardButton(text='Назад', callback_data='shutdown_back')
kb_admin_shutdown.add(button1_shutdown)

kb_admin_shutdown_confirm = InlineKeyboardMarkup(row_width=2)
button1_shutdown_confirm = InlineKeyboardButton(text='Назад', callback_data='shutdown_confirm_back')
kb_admin_shutdown_confirm.add(button1_shutdown_confirm)

kb_admin_restart_bot = InlineKeyboardMarkup(row_width=2)
button1_restart_bot = InlineKeyboardButton(text='Да', callback_data='restart_bot_yes')
button2_restart_bot = InlineKeyboardButton(text='Назад', callback_data='restart_bot_back')
kb_admin_restart_bot.add(button1_restart_bot).add(button2_restart_bot)

kb_admin_moysklad = InlineKeyboardMarkup(row_width=2)
button1_moysklad = InlineKeyboardButton(text='Обновить', callback_data='update_moysklad')
button2_moysklad = InlineKeyboardButton(text='Таймер обновления', callback_data='update_moysklad_timer')
button3_moysklad = InlineKeyboardButton(text='Назад', callback_data='moysklad_back')
kb_admin_moysklad.add(button1_moysklad).add(button2_moysklad).add(button3_moysklad)

kb_admin_update_moysklad_back = InlineKeyboardMarkup(row_width=2)
button1_update_moysklad_back = InlineKeyboardButton(text='Назад', callback_data='update_moysklad_back')
kb_admin_update_moysklad_back.add(button1_update_moysklad_back)

kb_admin_sales = InlineKeyboardMarkup(row_width=2)
button1_admin_sales = InlineKeyboardButton(text='Список акций', callback_data='admin_sales_list_view')
button2_admin_sales = InlineKeyboardButton(text='Добавить акцию', callback_data='admin_sales_add_sale')
button3_admin_sales = InlineKeyboardButton(text='Назад', callback_data='admin_sales_back')
kb_admin_sales.add(button1_admin_sales).add(button2_admin_sales).add(button3_admin_sales)

with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
    all_sales_json = f.read()
all_sales = json.loads(all_sales_json)

kbs_admin_sales_list = []
for i in range(len(all_sales["context"])):
    kb_admin_sales_list = InlineKeyboardMarkup(row_width=2)
    button1_admin_sales_list = InlineKeyboardButton(text=u'\u2B05\uFE0F', callback_data='admin_sales_list_previous_page')
    button2_admin_sales_list = InlineKeyboardButton(text=f'Страница {i+1}/{len(all_sales["context"])}',
                                                    callback_data='admin_sales_list_alert')
    button3_admin_sales_list = InlineKeyboardButton(text=u'\u27A1\uFE0F', callback_data='admin_sales_list_next_page')
    button4_admin_sales_list = InlineKeyboardButton(text='Изменить описание', callback_data='admin_sales_change_desc')
    button5_admin_sales_list = InlineKeyboardButton(text='Изменить фотографию',
                                                    callback_data='admin_sales_change_photo')
    button6_admin_sales_list = InlineKeyboardButton(text='Вкл/Выкл акцию', callback_data='admin_sales_switch_sale')
    button7_admin_sales_list = InlineKeyboardButton(text=u'Назад',
                                                    callback_data='admin_back_to_sales')
    kb_admin_sales_list.row(button1_admin_sales_list, button2_admin_sales_list, button3_admin_sales_list)\
        .add(button4_admin_sales_list).add(button5_admin_sales_list).add(button6_admin_sales_list)\
        .add(button7_admin_sales_list)
    kbs_admin_sales_list.append(kb_admin_sales_list)

kb_admin_sales_list_back = InlineKeyboardMarkup(row_width=2)
button1_sales_list_back = InlineKeyboardButton(text='Назад', callback_data='sales_list_back')
kb_admin_sales_list_back.add(button1_sales_list_back)

kb_admin_sale_add = InlineKeyboardMarkup(row_width=2)
button1_sale_add = InlineKeyboardButton(text='Сохранить', callback_data='sales_add_confirm')
button2_sale_add = InlineKeyboardButton(text='Отмена', callback_data='sales_add_cancel')
kb_admin_sale_add.add(button1_sale_add).add(button2_sale_add)

kb_admin_users_db = InlineKeyboardMarkup(row_width=2)
button1_users_db = InlineKeyboardButton(text='МойСклад', callback_data='users_moysklad')
button2_users_db = InlineKeyboardButton(text='Бот', callback_data='users_bot')
button3_users_db = InlineKeyboardButton(text='Назад', callback_data='users_db_back')
kb_admin_users_db.add(button1_users_db).add(button2_users_db).add(button3_users_db)

kb_admin_users_db_back = InlineKeyboardMarkup(row_width=2)
button1_users_db_back = InlineKeyboardButton(text='Назад', callback_data='users_db_in_back')
kb_admin_users_db_back.add(button1_users_db_back)
