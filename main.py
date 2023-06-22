from datetime import datetime
import time

import requests
from aiogram import Bot, Dispatcher, executor, types
import vk_api

import config

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)


# Функция эхо бота для проверки работоспособности и получения ид чата
@dp.message_handler(commands=['0'])
async def echo_mess(message: types.Message):
    await bot.send_message(message.chat.id, "Бот работает")
    # await bot.send_message(message.chat.id, message.chat.id)
    print(message.chat.id)
    print("Сообщение отправлено")


session = vk_api.VkApi(token=config.access_token)
vk_me = session.get_api()

# Прочитаем файл с айдишниками сообщений уже отправленных ранее
with open("list.txt", "r") as file:
    text = file.read()
    # Преобразуем в список
    new_text = text.split(" ")
    list_msg_id = new_text
    file.close()


# Функция отправки сообщения в ВК
# Не используется
def send_vk(msg):
    vk_me.messages.send(user_id=config.vk_user_id_for_send_mgs, message=msg, random_id=0)


# Функция отправки сообщения в телеграмм
def send_telegram(text_to_bot):
    print(f"Функция отправки сообщения в телеграмм. {text_to_bot}")
    url = f'https://api.telegram.org/bot{config.BOT_API_TOKEN}/sendMessage'
    # Будем отправлять два сообщения, в личку и в чат
    data_to_chat = {
        'chat_id': config.chat_id,
        'text': text_to_bot,
        'parse_mode': 'HTML'
    }
    requests.post(url=url, data=data_to_chat)

    data_to_user = {
        'chat_id': config.user_id,
        'text': text_to_bot,
        'parse_mode': 'HTML'
    }
    requests.post(url=url, data=data_to_user)


def start_parsing():
    print("Основная функция запущена")
    # Список сообщений взятый из файла
    global list_msg_id
    # Новый список ид сообщений для сверки
    new_list_msg_id = []
    # Запишем в переменную ответ от api
    # config.vk_chat_id здесь ид чата 2000000000 + ид чата
    gegemony = vk_me.messages.getHistory(count=200, user_id=config.vk_chat_id)
    # Делаем перебор списка сообщений
    for msg in gegemony["items"]:
        # Ищем совпадения с ид юзером сообщения которого нам нужны
        if msg['from_id'] == config.target_user_id:
            # Добавляем ид сообщения в новый список со всеми ид сообщений этого пользователя
            new_list_msg_id.append(str(msg['id']))
            print(msg)
            print(msg["text"])
    print(f"Новый список id сообщений: {new_list_msg_id}")
    # Развернем список для его правильного отображения
    new_list_msg_id.reverse()
    # Сверяем новый список со старым
    if new_list_msg_id == list_msg_id:
        print("Списки совпадают")
    else:
        print("Списки не совпадают")
        # Если списки не совпадают делаем перебор нового списка
        for msg_id in new_list_msg_id:
            # Ищем есть ли ид в прошлом списке
            if list_msg_id.count(msg_id) == 0:
                print(f"Есть новое сообщение: {msg_id}")
                # Если обнаружен новый ид, перебираем сообщения с поиском этого им
                # TODO попробовать найти более простой и быстрый способ
                for key in gegemony["items"]:
                    # для сверки ид из списка надо преобразовать к числу
                    if key['id'] == int(msg_id):
                        #  Преобразуем в нормальную дату, изначально используются секунды
                        second = int(key['date'])
                        dt = datetime.fromtimestamp(second)
                        # Проверка на ключ reply. Если был дан ответ на чей-то вопрос
                        # !!! Имя пользователей не хранится в ответе. На примере я прописал имя вручную
                        try:
                            reply_text = key['reply_message']['text']
                            text_msg = f"Виталий Харченко: \n" \
                                       f"{dt} \n" \
                                       f"{key['text']} \n" \
                                       f"------------------------- \n" \
                                       f"В ответ на: \n" \
                                       f"{reply_text}"
                        except KeyError:
                            text_msg = f"Виталий Харченко: \n" \
                                       f"{dt} \n" \
                                       f"{key['text']} \n"

                        # Отправим сообщение в телеграмм
                        send_telegram(text_msg)
                        # Отправим сообщение в вк
                        send_vk(text_msg)
                print(msg_id)

    # Запись в файл нового списка ид сообщений
    h = ' '.join(new_list_msg_id)
    file1 = open("list.txt", "w")
    file1.write(h)
    file1.close()

    # Обновить список в памяти
    list_msg_id = new_list_msg_id


def main():
    # send_telegram("Бот запущен")
    # send("Бот запущен")
    # Запустим сразу
    start_parsing()
    # И бесконечный цикл на 3 минуты
    while True:
        time.sleep(180)
        start_parsing()


if __name__ == '__main__':
    # !!! Заменить строчки для эхо бота
    # executor.start_polling(dp, skip_updates=True)
    main()
