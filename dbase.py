import psycopg2
from config import host, user, password, db_name

connection = psycopg2.connect(
    host = host, user = user, password = password, database = db_name, port = "5432"
)
connection.autocommit = True


def create_table():
    """СОЗДАНИЕ ТАБЛИЦЫ USERS (НАЙДЕННЫЕ ПОЛЬЗОВАТЕЛИ)"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id serial,
                first_name varchar(50) NOT NULL,
                last_name varchar(25) NOT NULL,
                vk_id integer NOT NULL PRIMARY KEY,
                seen_users boolean);"""
            # """DROP TABLE IF EXISTS users CASCADE;"""
        )
    print("[INFO] Table USERS was created.")


def insert_data_users(first_name, last_name, vk_id):
    """ВСТАВКА ДАННЫХ В ТАБЛИЦУ USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO users (first_name, last_name, vk_id, seen_users) 
                     VALUES ('{first_name}', '{last_name}', '{vk_id}', False);"""
        )

    """ВЫБОРКА ВСЕХ VK_ID"""


def vk_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT vk_id From users;
            """
        )
        vk_user = cursor.fetchall()
        vk_user_list = []
        for i in vk_user:
            e = i[0]
            vk_user_list.append(e)
        return vk_user_list

    """ВЫБОРКА ВСЕХ ПРОСМОТРЕННЫХ ID"""


def users_seens():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT vk_id, first_name, last_name From users 
            where seen_users = False;
            """
        )
        id_user = cursor.fetchmany(3)
        for p in id_user:
            cursor.execute(
                """
                     UPDATE users
                     SET  seen_users = True
                     WHERE  vk_id  = %s 
                     ;
                     """,
                (p[0],),
            )
        return id_user
