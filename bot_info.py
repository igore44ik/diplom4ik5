import requests
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dbase import create_table, insert_data_users, vk_users, users_seens


class Application (object):
    def __init__(self, token_group, token_my):
        self.token_group = token_group
        self.token_my = token_my
        self.api = vk_api.VkApi(token = self.token_group)  # АВТОРИЗАЦИЯ СООБЩЕСТВА

    # функция отправки сообщений

    def write_msg(self, user_id, message):
        self.api.method('messages.send',
                          {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

    # ФУНКЦИЯ ДЛЯ СБОРА ИНФОРМАЦИИ О ПОЛЬЗОВАТЕЛЕ
    def id_info(self, id, tok_group):
        id_params = []
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': tok_group,
                  'user_ids': id,
                  'fields': 'sex, bdate, city, relation',
                  'v': '5.131'}
        repl = requests.get(url, params = params)
        response = repl.json()
        sex_id = response['response'][0]['sex']  # определяем пол пользователя
        if sex_id == 1:
            sex_id = 2
        if sex_id == 2:
            sex_id = 1
        id_params.append(sex_id)  # добавляем параметр в список
        try:
            bdate_id = response['response'][0]['bdate']  # определяем возраст пользователя
            id_params.append(bdate_id[-4:])  # добавляем параметр в список
        except KeyError:
            self.write_msg(id, 'Введите год вашего рождения ' )
            longpoll = VkLongPoll(self.api)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    bdate_id = event.text
                    id_params.append(str(bdate_id))  # добавляем параметр в список
                    break
        try:
            city_id = response['response'][0]['city']['title'].lower()  # определяем город пользователя
            id_params.append(city_id)  # добавляем параметр в список
        except KeyError:
            self.write_msg(id, 'Введите ваш город ')
            longpoll = VkLongPoll(self.api)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    bdate_id = event.text
                    id_params.append(str(bdate_id.lower()))  # добавляем параметр в список
                    break
        relation_id = response['response'][0]['relation']  # определяем статус пользователя
        id_params.append(relation_id)  # добавляем параметр в список
        return id_params

    # ФУНКЦИЯ ДЛЯ ПОИСКА ЛЮДЕЙ ПО ЗАДАННЫМ ПАРАМЕТРАМ
    def search_users(self, id_params) -> list[dict]:
        url = f'https://api.vk.com/method/users.search'
        params = {'access_token': self.token_my,
                  'v': '5.131',
                  'sex': id_params[0],
                  'birth_year': id_params[1],
                  'hometown': id_params[2],
                  'fields': 'is_closed, id, first_name, last_name, bdate, city, home_town',
                  'status': id_params[3],
                  'count': 500,
                  'sort': 0,
                  'offset': 1
                  }
        resp = requests.get(url, params = params)
        resp_json = resp.json()
        try:
            characteristic = resp_json['response']
        except KeyError:
            print(f'Ошибка получения данных API {self.token_my} (по ранее полученным данным) '
                      f', проверьте валидность токенов, реализованных методов')
        characteristic_id = characteristic['items']
        list_seen_users = []
        for person_dict in characteristic_id:
            if not person_dict.get('is_closed'):
                first_name = person_dict.get('first_name')
                last_name = person_dict.get('last_name')
                vk_id = str(person_dict.get('id'))
                vk_link = 'vk.com/id' + str(person_dict.get('id'))
                if int(vk_id) not in vk_users():
                    insert_data_users(first_name, last_name, vk_id)
            else:
                continue
            list_seen_users.append({'first_name': first_name, 'last_name': last_name, 'id': vk_id, 'link': vk_link})
        return list_seen_users

    # ФУНКЦИЯ ДЛЯ ПОЛУЧЕНЯ ФОТО
    def get_photos_id(self, id):
        url = 'https://api.vk.com/method/photos.getAll'
        params = {'access_token': self.token_my,
                  'type': 'album',
                  'owner_id': id,
                  'extended': 1,
                  'count': 25,
                  'v': '5.131'}
        resp = requests.get(url, params = params)
        dict_photos = dict()
        resp_json = resp.json()
        try:
            characteristic = resp_json['response']
        except KeyError:
            print(f'Ошибка получения данных API {id} (фотографии пользователя) '
                    f', проверьте валидность токенов, либо наличие данных по реализованным методам' )
        characteristic_id = characteristic['items']
        for i in characteristic_id:
            photo_id = str(i.get('id'))
            i_likes = i.get('likes')
            if i_likes.get('count'):
                likes = i_likes.get('count')
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse = True)
        return list_of_ids[:3]  # выборка трёх фотографий

    # ФУНКЦИЯ ДЛЯ ОТПРАВКИ ФОТО
    def send_photos(self, user_id, owner_id, media_id):
        self.api.method('messages.send', {'user_id': user_id,
                                            'access_token': self.token_my,
                                            'attachment': f'photo{owner_id}_{media_id}',
                                            'random_id': 0})

    # ФУНКЦИЯ ПОКАЗЫВАЕТ ПО ТРИ ПОЛЬЗОВАТЕЛЯ, СООТВЕТСТВУЮЩИЗ ПОИСКУ
    def demonstrstion(self, id_id, length):
        i = 0
        while i < 3:
            fotos = self.get_photos_id(length[i][0])
            vk_link = str(length[i][1]) + '  ' + str(length[i][2]) + '    ' + 'vk.com/id' + str(length[i][0])
            self.write_msg(id_id, vk_link)
            for f in range(3):
                try:
                    self.send_photos(id_id, length[i][0], fotos[f][1])
                except IndexError:
                    continue
            i += 1

    # ЛОГИКА БОТА
    def run(self):
        longpoll = VkLongPoll(self.api)  # РАБОТА С СООБЩЕНИЯМИ
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    if request.lower() == 'привет':
                        self.write_msg(event.user_id, 'Привет, хочешь найти себе пару? (Да/Нет)')
                        for event in longpoll.listen ():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                request = event.text
                                if request.lower() == 'да':
                                    self.write_msg(event.user_id, 'Проверяю, достаточно ли параметров для поиска...')
                                    create_table()
                                    user_info = self.id_info(event.user_id, self.token_group)
                                    params_id = user_info
                                    self.search_users(params_id)
                                    length = users_seens()
                                    id_id = event.user_id
                                    self.demonstrstion(id_id, length)
                                    self.write_msg(event.user_id, 'Показать еще подходящих пользователей ? ДА/НЕТ')
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                            request = event.text
                                            if request.lower() == 'да':
                                                length = users_seens()
                                                self.demonstrstion(id_id, length)
                                                self.write_msg(event.user_id,
                                                                 'Показать еще подходящих пользователей ? ДА/НЕТ' )
                                            elif request.lower() == 'нет':
                                                self.write_msg(event.user_id, 'Как захочешь,заходи!')
                                            break
                                elif request.lower() == 'нет':
                                    self.write_msg(event.user_id, 'Как захочешь,заходи!')
                                    break
                                else:
                                    self.write_msg(event.user_id, 'Ответьте "ДА" или "Нет" ')
                    elif request.lower() == 'пока':
                        break
                    else:
                        self.write_msg(event.user_id,
                                         'Напишите боту "Привет" для начала работы или "Пока" для выхода' )
