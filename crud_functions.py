import sqlite3

connection = sqlite3.connect('Products.db')


def initiate_db():
    with connection:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Products(id INTEGER PRIMARY KEY,'
                       'title TEXT NOT NULL,'
                       'description TEXT,'
                       'price INTEGER NOT NULL,'
                       'pics BLOB)')

        #cursor.execute('DELETE FROM Products')  # удалим старые записи

        cursor.execute('CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY,'
                       'username TEXT NOT NULL,'
                       'email TEXT NOT NULL,'
                       'age INTEGER NOT NULL,'
                       'balance INTEGER NOT NULL)')
        #cursor.execute('DELETE FROM Users')

        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM Products')
        if cursor.fetchone()[0] == 0:
            # заполним таблицу
            for i in range(1, 5):
                try:
                    with open(f'pic{i}.png', 'rb') as pic:
                        cursor.execute('INSERT INTO Products(title, description, price, pics) VALUES(?,?,?,?)',
                                       (f'Продукт{i}', f'Описание{i}', i * 100, pic.read()))
                except Exception as err:
                    print(err)
        connection.commit()

def is_included(username) -> bool:
    with connection:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM Users WHERE username = ?', (username,))
        return cursor.fetchone()[0] == 1

def add_user(username, email, age):
    with connection:
        cursor = connection.cursor()
        sql = (
            f"INSERT INTO Users (username, email, age, balance) VALUES ('{username}', '{email}', {age}, 1000)")
        if is_included(username) == False:
            cursor.execute(sql)


def get_all_products():
    result = []
    with connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Products')

        result = cursor.fetchall()

    return result


if __name__ == '__main__':
    initiate_db()
    for i in get_all_products():
        print(i[4])