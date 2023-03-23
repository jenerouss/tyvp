import json

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

with open("config/клавиатуры и типы/buttons.json", 'r', encoding='utf-8') as f:
    all_products_json = f.read()
all_products = json.loads(all_products_json)

with open("config/акции/actions.json", 'r', encoding='utf-8') as f:
    all_actions_json = f.read()
all_actions = json.loads(all_actions_json)


kb_main = InlineKeyboardMarkup(row_width=2)
button1main = InlineKeyboardButton(text=u'\U0001F4C4Ассортимент', callback_data='assortiment')
button2main = InlineKeyboardButton(text=u'\U0001F525Акции', callback_data='actions')
button3main = InlineKeyboardButton(text=u'\U0001F4B8Бонусная программа', callback_data='bonuses')
button4main = InlineKeyboardButton(text=u'\U0001F4ACСвязаться с администратором', url='https://t.me/Areuokayshop')
button5main = InlineKeyboardButton(text=u'\U0001F5C4База данных', callback_data='data_base')
kb_main.add(button1main).add(button2main).add(button3main).add(button4main).add(button5main)


kb_assortiment = InlineKeyboardMarkup(row_width=2)
button0predassortiment = InlineKeyboardButton(text=u'\U0001F50DПоиск по всей продукции',
                                              switch_inline_query_current_chat='')
button1predassortiment = InlineKeyboardButton(text=u'\U0001F4A8Кальянная продукция', callback_data='hookahprod')
button2predassortiment = InlineKeyboardButton(text=u'\U0001F4A7Вейп продукция', callback_data='vapeprod')
button3predassortiment = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main')
kb_assortiment.add(button0predassortiment).row(button1predassortiment,button2predassortiment).add(button3predassortiment)


kb_hookah_assort = InlineKeyboardMarkup(row_width=2)
button0hookah = InlineKeyboardButton(text=u'\U0001F50DПоиск по всей кальянной продукции',
                                          switch_inline_query_current_chat='')
button1hookah = InlineKeyboardButton(text=u'\U0001F4A8Табак', callback_data='tabak')
button2hookah = InlineKeyboardButton(text=u'\U0001F9E9Комплектующие для кальяна', callback_data='hookahitems')
button3hookah = InlineKeyboardButton(text=u'\u26F2\uFE0FКальяны', callback_data='hookahs')
button4hookah = InlineKeyboardButton(text=u'\u25FCУголь', callback_data='coal')
button5hookah = InlineKeyboardButton(text=u'\U0001F4B2Услуги', callback_data='service')
button6hookah = InlineKeyboardButton(text=u'\U0001F5B2Чаши', callback_data='chasha')
button7hookah = InlineKeyboardButton(text=u'\U0001F962Щипцы', callback_data='shipci')
button8hookah = InlineKeyboardButton(text=u'\U0001F519Назад', callback_data='assort_back')
button9hookah = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main')
kb_hookah_assort.add(button0hookah).row(button1hookah,button4hookah).row(button6hookah,button7hookah)\
    .row(button3hookah,button5hookah).add(button2hookah).add(button8hookah).add(button9hookah)


kb_vape_assort = InlineKeyboardMarkup(row_width=2)
button0vape = InlineKeyboardButton(text=u'\U0001F50DПоиск по всей вейп продукции',
                                        switch_inline_query_current_chat='')
button1vape = InlineKeyboardButton(text=u'\U0001F4A7Жидкости', callback_data='zidkosti')
button2vape = InlineKeyboardButton(text=u'\U0001F58AУстройства', callback_data='devices')
button3vape = InlineKeyboardButton(text=u'\U0001F58DОдноразки', callback_data='odnorazki')
button4vape = InlineKeyboardButton(text=u'\U0001F6E0Расходники устройств', callback_data='cartriges')
button5vape = InlineKeyboardButton(text=u'\U0001F519Назад', callback_data='assort_back')
button6vape = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main')
kb_vape_assort.add(button0vape).row(button1vape,button3vape).row(button2vape,button4vape).add(button5vape).add(button6vape)


kb_tabak = InlineKeyboardMarkup(row_width=2)

tabak_len = len(all_products["табак"])
buttons_tabak = []
buttons_tabak.append(InlineKeyboardButton(text='Весь ассортимент', callback_data='all_tabak'))
for j in range(tabak_len):
    buttons_tabak.append(InlineKeyboardButton(text=all_products["табак"][j], callback_data=f'{all_products["табак"][j]}'
                                                                                           f'табак'))
buttons_tabak.append(InlineKeyboardButton(text=u'\U0001F519Назад', callback_data='hookah_back'))
buttons_tabak.append(InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main'))
kb_tabak.add(buttons_tabak[0])
k = 1
while k <= tabak_len:
    if tabak_len - k > 1:
        kb_tabak.row(buttons_tabak[k], buttons_tabak[k+1], buttons_tabak[k+2])
        k += 3
    elif tabak_len - k > 0:
        kb_tabak.row(buttons_tabak[k], buttons_tabak[k+1])
        k += 2
    else:
        kb_tabak.add(buttons_tabak[k])
        k += 1

kb_tabak.add(buttons_tabak[tabak_len+1]).add(buttons_tabak[tabak_len+2])


kb_zizi = InlineKeyboardMarkup(row_width=2)

zizi_len = len(all_products["жидкости"])
buttons_zizi = []
buttons_zizi.append(InlineKeyboardButton(text='Весь ассортимент', callback_data='all_zizi'))
for j in range(zizi_len):
    buttons_zizi.append(InlineKeyboardButton(text=all_products["жидкости"][j],
                                             callback_data=f'{all_products["жидкости"][j]}жидкости'))
buttons_zizi.append(InlineKeyboardButton(text=u'\U0001F519Назад', callback_data='vape_back'))
buttons_zizi.append(InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main'))
kb_zizi.add(buttons_zizi[0])
k = 1
while k <= zizi_len:
    if zizi_len - k > 1:
        kb_zizi.row(buttons_zizi[k], buttons_zizi[k+1], buttons_zizi[k+2])
        k += 3
    elif zizi_len - k > 0:
        kb_zizi.row(buttons_zizi[k], buttons_zizi[k+1])
        k += 2
    else:
        kb_zizi.add(buttons_zizi[k])
        k += 1
kb_zizi.add(buttons_zizi[zizi_len+1]).add(buttons_zizi[zizi_len+2])


kb_devices = InlineKeyboardMarkup(row_width=2)

devices_len = len(all_products["устройства"])
buttons_devices = []
buttons_devices.append(InlineKeyboardButton(text='Весь ассортимент', callback_data='all_devices'))
for j in range(devices_len):
    buttons_devices.append(InlineKeyboardButton(text=all_products["устройства"][j],
                                                callback_data=f'{all_products["устройства"][j]}устройства'))
buttons_devices.append(InlineKeyboardButton(text=u'\U0001F519Назад', callback_data='vape_back'))
buttons_devices.append(InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main'))
kb_devices.add(buttons_devices[0])
k = 1
while k <= devices_len:
    if devices_len - k > 1:
        kb_devices.row(buttons_devices[k], buttons_devices[k+1], buttons_devices[k+2])
        k += 3
    elif devices_len - k > 0:
        kb_devices.row(buttons_devices[k], buttons_devices[k+1])
        k += 2
    else:
        kb_devices.add(buttons_devices[k])
        k += 1
kb_devices.add(buttons_devices[devices_len+1]).add(buttons_devices[devices_len+2])


kb_odnorazki = InlineKeyboardMarkup(row_width=2)

odnorazki_len = len(all_products["одноразки"])
buttons_odnorazki = []
buttons_odnorazki.append(InlineKeyboardButton(text='Весь ассортимент', callback_data='all_odnorazki'))
for j in range(odnorazki_len):
    buttons_odnorazki.append(InlineKeyboardButton(text=all_products["одноразки"][j],
                                                  callback_data=f'{all_products["одноразки"][j]}одноразки'))
buttons_odnorazki.append(InlineKeyboardButton(text=u'\U0001F519Назад', callback_data='vape_back'))
buttons_odnorazki.append(InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main'))
kb_odnorazki.add(buttons_odnorazki[0])
k = 1
while k <= odnorazki_len:
    if odnorazki_len - k > 1:
        kb_odnorazki.row(buttons_odnorazki[k], buttons_odnorazki[k+1], buttons_odnorazki[k+2])
        k += 3
    elif odnorazki_len - k > 0:
        kb_odnorazki.row(buttons_odnorazki[k], buttons_odnorazki[k+1])
        k += 2
    else:
        kb_odnorazki.add(buttons_odnorazki[k])
        k += 1
kb_odnorazki.add(buttons_odnorazki[odnorazki_len+1]).add(buttons_odnorazki[odnorazki_len+2])


kb_cartriges = InlineKeyboardMarkup(row_width=2)

cartriges_len = len(all_products["расходники"])
buttons_cartriges = []
buttons_cartriges.append(InlineKeyboardButton(text='Весь ассортимент', callback_data='all_cartriges'))
for j in range(cartriges_len):
    buttons_cartriges.append(InlineKeyboardButton(text=all_products["расходники"][j],
                                                  callback_data=f'{all_products["расходники"][j]}расходники'))
buttons_cartriges.append(InlineKeyboardButton(text=u'\U0001F519Назад', callback_data='vape_back'))
buttons_cartriges.append(InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main'))
kb_cartriges.add(buttons_cartriges[0])
k = 1
while k <= cartriges_len:
    if cartriges_len - k > 1:
        kb_cartriges.row(buttons_cartriges[k], buttons_cartriges[k+1], buttons_cartriges[k+2])
        k += 3
    elif cartriges_len - k > 0:
        kb_cartriges.row(buttons_cartriges[k], buttons_cartriges[k+1])
        k += 2
    else:
        kb_cartriges.add(buttons_cartriges[k])
        k += 1
kb_cartriges.add(buttons_cartriges[cartriges_len+1]).add(buttons_cartriges[cartriges_len+2])

all_active_actions = []
for i in all_actions["context"]:
    if i['action']['active'] == "1":
        all_active_actions.append(i)
all_active_actions_len = len(all_active_actions)
kbs_actions = []
for i in range(all_active_actions_len):
    kb_actions = InlineKeyboardMarkup(row_width=2)
    button1_actions = InlineKeyboardButton(text=u'\u2B05\uFE0F', callback_data='actions_previous_page')
    button2_actions = InlineKeyboardButton(text=f'Страница {i+1}/{all_active_actions_len}', callback_data='actions_alert')
    button3_actions = InlineKeyboardButton(text=u'\u27A1\uFE0F', callback_data='actions_next_page')
    button4_actions = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main')
    kb_actions.row(button1_actions,button2_actions,button3_actions).add(button4_actions)
    kbs_actions.append(kb_actions)

kb_bonuses = InlineKeyboardMarkup(row_width=2)
button1bonuses = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main')
kb_bonuses.add(button1bonuses)

kb_bonuses_logined = InlineKeyboardMarkup(row_width=2)
# Todo:
# button1bonuseslog = InlineKeyboardButton(text='📈История покупок', callback_data='buy_history')
button2bonuseslog = InlineKeyboardButton(text=u'\u274CВыйти из учетной записи', callback_data='log_out')
button3bonuseslog = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main')
# Todo:
# kb_bonuses_logined.add(button1bonuseslog)
kb_bonuses_logined.add(button2bonuseslog).add(button3bonuseslog)

kb_bonuses_logined_no_name = InlineKeyboardMarkup(row_width=2)
# Todo:
# button1bonuseslog_no_name = InlineKeyboardButton(text='❇️Зарегестрироваться', callback_data='register_in_bonus')
button2bonuseslog_no_name = InlineKeyboardButton(text=u'\u274CВыйти из учетной записи', callback_data='log_out')
button3bonuseslog_no_name = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню',
                                                 callback_data='back_to_main')
# kb_bonuses_logined_no_name.add(button1bonuseslog_no_name)
kb_bonuses_logined_no_name.add(button2bonuseslog_no_name).add(button3bonuseslog_no_name)

kb_base = InlineKeyboardMarkup(row_width=2)
button1base = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main')
kb_base.add(button1base)

kb_via_bot = InlineKeyboardMarkup(row_width=2)
button1via = InlineKeyboardButton(text=u'\U0001F50DПопробовать в другом чате', switch_inline_query='')
button2via = InlineKeyboardButton(text=u'\u274CУдалить сообщения', callback_data='via_back')
kb_via_bot.add(button1via).add(button2via)

kb_to_main = InlineKeyboardMarkup(row_width=2)
button1to_main = InlineKeyboardButton(text=u'\U0001F51AВернуться в главное меню', callback_data='back_to_main')
button2to_main = InlineKeyboardButton(text=u'\u274CУдалить сообщения', callback_data='via_back')
kb_to_main.add(button1to_main).add(button2to_main)

kb_admin_enter = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
button1_admin_enter = KeyboardButton(text='Войти в админ панель')
kb_admin_enter.add(button1_admin_enter)