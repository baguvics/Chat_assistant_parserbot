import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()
DB_PATH = os.environ.get('DB_PATH')

# Создание подключения к базе данных
def create_bd():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Создание таблицы "Человек"
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS Person ( 
                id INTEGER PRIMARY KEY, 
                telegramId INTEGER UNIQUE, 
                fullName TEXT, 
                phone TEXT 
            ) 
        ''')

        # Создание таблицы "Предложения"
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS Suggestions ( 
                id INTEGER PRIMARY KEY, 
                personId INTEGER, 
                suggestionText TEXT, 
                FOREIGN KEY (personId) REFERENCES Person(id) 
            ) 
        ''')

        # Создание таблицы "ВопросОтвет"
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS QA ( 
                id INTEGER PRIMARY KEY, 
                question TEXT, 
                answer TEXT 
            ) 
        ''')

        # Создание таблицы "Новости"
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS News ( 
                id INTEGER PRIMARY KEY, 
                newsText TEXT 
            ) 
        ''')
        # Создание таблицы "Мероприятия"
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS Events ( 
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                date TEXT 
            ) 
        ''')

        # Создание таблицы "МероприятияЧеловек"
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS EventPerson ( 
                id INTEGER PRIMARY KEY, 
                eventId INTEGER, 
                personId INTEGER, 
                FOREIGN KEY (eventId) REFERENCES Events(id), 
                FOREIGN KEY (personId) REFERENCES Person(id) 
            ) 
        ''')

        # Сохранение изменений и закрытие соединения
        conn.commit()
        conn.close()


