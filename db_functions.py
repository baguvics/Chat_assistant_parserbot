import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()
DB_PATH = os.environ.get('DB_PATH')

def execute_query(query, values=None, fetch_all=False):
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
    execute_query(query, (event_name, event_date))


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

    execute_query(update_query, tuple(update_values))


def get_all_events():
    query = 'SELECT * FROM Events'
    return execute_query(query, fetch_all=True)


def delete_event_by_id(event_id):
    delete_query = 'DELETE FROM Events WHERE id = ?'
    execute_query(delete_query, (event_id,))

# people
def add_person_to_db(telegram_id, full_name, phone):
    query = ''' 
        INSERT INTO Person (telegramId, fullName, phone) 
        VALUES (?, ?, ?) 
    '''
    execute_query(query, (telegram_id, full_name, phone))


def delete_person_by_id(person_id):  # admin
    query = 'DELETE FROM Person WHERE id = ?'
    execute_query(query, (person_id,))


def update_person_by_id(person_id, new_full_name=None, new_phone=None):  # admin
    update_query = 'UPDATE Person SET'
    update_values = []

    if new_full_name is not None:
        update_query += ' fullName = ?,'
        update_values.append(new_full_name)

    if new_phone is not None:
        update_query += ' phone = ?,'
        update_values.append(new_phone)

    update_query = update_query.rstrip(',')

    update_query += ' WHERE id = ?'
    update_values.append(person_id)

    execute_query(update_query, tuple(update_values))


def get_all_people():  # admin
    query = 'SELECT * FROM Person'
    print(execute_query(query, fetch_all=True))
    return execute_query(query, fetch_all=True)


# Предложения


def add_suggestion_to_db(person_id, suggestion_text):
    query = ''' 
        INSERT INTO Suggestions (personId, suggestionText) 
        VALUES (?, ?) 
    '''
    execute_query(query, (person_id, suggestion_text))


def get_all_suggestions():  # admin
    query = 'SELECT * FROM Suggestions'
    return execute_query(query, fetch_all=True)


# QA


def get_all_people():  # admin
    query = 'SELECT * FROM Person'
    return execute_query(query, fetch_all=True)


def add_qa_to_db(question, answer):
    query = ''' 
        INSERT INTO QA (question, answer) 
        VALUES (?, ?) 
    '''
    execute_query(query, (question, answer))


def get_all_qa():  # admin
    query = 'SELECT * FROM QA'
    return execute_query(query, fetch_all=True)


def update_qa_by_id(qa_id, new_question=None, new_answer=None):  # admin
    update_query = 'UPDATE QA SET'
    update_values = []

    if new_question is not None:
        update_query += ' question = ?,'
        update_values.append(new_question)

    if new_answer is not None:
        update_query += ' answer = ?,'
        update_values.append(new_answer)

    update_query = update_query.rstrip(',')

    update_query += ' WHERE id = ?'
    update_values.append(qa_id)

    execute_query(update_query, tuple(update_values))


def delete_qa_by_id(qa_id):  # admin
    query = 'DELETE FROM QA WHERE id = ?'
    execute_query(query, (qa_id,))


# Мероприятие - человек


def add_event_person_to_db(event_id, person_id):
    query = ''' 
        INSERT INTO EventPerson (eventId, personId) 
        VALUES (?, ?) 
    '''
    execute_query(query, (event_id, person_id))


def get_all_event_person():  # admin
    query = 'SELECT * FROM EventPerson'
    print(execute_query(query, fetch_all=True))
    return execute_query(query, fetch_all=True)


def update_event_person_by_id(event_person_id, new_event_id=None, new_person_id=None):  # admin
    update_query = 'UPDATE EventPerson SET'
    update_values = []

    if new_event_id is not None:
        update_query += ' eventId = ?,'
        update_values.append(new_event_id)

    if new_person_id is not None:
        update_query += ' personId = ?,'
        update_values.append(new_person_id)

    update_query = update_query.rstrip(',')

    update_query += ' WHERE id = ?'
    update_values.append(event_person_id)

    execute_query(update_query, tuple(update_values))


def delete_event_person_by_id(event_person_id):
    query = 'DELETE FROM EventPerson WHERE id = ?'
    execute_query(query, (event_person_id,))