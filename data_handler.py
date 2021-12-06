import csv
import os
import database_common
from datetime import datetime


@database_common.connection_handler
def import_all_questions(cursor):
    query = '''
        SELECT * FROM question
    '''
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_question_id(cursor, question_id):
    query = '''
        SELECT * FROM answer
        WHERE question_id = %s
        ORDER BY vote_number DESC'''
    # needs sorting
    cursor.execute(query, (question_id, ))
    return cursor.fetchall()


@database_common.connection_handler
def get_question_by_id(cursor, question_id):
    query = '''
        SELECT * FROM question
        WHERE id = %s'''
    cursor.execute(query, (question_id, ))
    return cursor.fetchone()


@database_common.connection_handler
def add_question(cursor, data):
    timestamp = datetime.now()
    query = '''
            INSERT INTO question(submission_time, view_number, vote_number, title, message, image)
            VALUES(%(subtime)s, %(view)s, %(vote)s, %(title)s, %(message)s, %(image)s)
        '''
    cursor.execute(query, {
        "subtime": timestamp,
        "view": 0,
        "vote": 0,
        "title": data["title"],
        "message": data["message"],
        "image": data["image"]})


def voting(database, data_index, vote):
    vote_number = int(database[data_index]['vote_number'])
    vote_number += 1 if vote == 'up' else (-1 if vote == 'down' else 0)
    database[data_index]['vote_number'] = vote_number
    return database


def delete_pictures(question_id, folder):
    all_answers = data_import(DATA_FILE_PATH_ANSWER)
    to_delete = list(filter(lambda x: x['question_id'] == question_id, all_answers))
    files = [f['image'] for f in to_delete]
    for file in files:
        try:
            os.remove(os.path.join(folder, file))
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    pass
