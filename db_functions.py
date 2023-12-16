import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()
DB_PATH = os.environ.get('DB_PATH')

def execute_query_events(query, values=None, fetch_all=False):
    # Создаем подключение к базе данных
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Выполняем запрос
    if values is not None:
        cursor.execute(query, values)
    else:
        cursor.execute(query)

        # Если нужно получить результат, возвращаем его
    result = cursor.fetchall() if fetch_all else None

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    return result


def add_event_to_db(event_name, event_date):
    query = ''' 
        INSERT INTO Events (name, date) 
        VALUES (?, ?) 
    '''
    execute_query_events(query, (event_name, event_date))


def update_event_by_id(event_id, new_name=None, new_date=None):
    update_query = 'UPDATE Events SET'
    update_values = []

    if new_name is not None:
        update_query += ' name = ?,'
        update_values.append(new_name)

    if new_date is not None:
        update_query += ' date = ?,'
        update_values.append(new_date)

    update_query = update_query.rstrip(',')

    update_query += ' WHERE id = ?'
    update_values.append(event_id)

    execute_query_events(update_query, tuple(update_values))


def get_all_events():
    query = 'SELECT * FROM Events'
    return execute_query_events(query, fetch_all=True)


def delete_event_by_id(event_id):
    delete_query = 'DELETE FROM Events WHERE id = ?'
    execute_query_events(delete_query, (event_id,))
