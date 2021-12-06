import csv
import os
import database_common
import datetime as dt


def round_seconds(obj: dt.datetime) -> dt.datetime:
    if obj.microsecond >= 500_000:
        obj += dt.timedelta(seconds=1)
    return obj.replace(microsecond=0)


@database_common.connection_handler
def import_all_questions(cursor):
    query = '''
        SELECT * FROM question;'''
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_question_id(cursor, question_id):
    query = '''
        SELECT * FROM answer
        WHERE question_id = %s
        ORDER BY vote_number DESC;'''
    # needs sorting
    cursor.execute(query, (question_id, ))
    return cursor.fetchall()


@database_common.connection_handler
def get_question_by_id(cursor, question_id):
    query = '''
        SELECT * FROM question
        WHERE id = %s;'''
    cursor.execute(query, (question_id, ))
    return cursor.fetchone()


@database_common.connection_handler
def add_question(cursor, data):
    timestamp = round_seconds(dt.datetime.now())
    if "image" not in data.keys():
        data["image"] = ""
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


@database_common.connection_handler
def data_export(filename, dict_data, header):
    with open(filename, "w", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)


@database_common.connection_handler
def update_question(cursor, question_data):
    query = '''
            UPDATE question
            SET title = %(title)s, message = %(message)s
            WHERE id = %(id)s'''
    cursor.execute(query, {"title": question_data["title"],
                           "message": question_data["message"],
                           "id": question_data["id"]})


@database_common.connection_handler
def delete_question(cursor, question_id):
    query = '''
        DELETE FROM question
        WHERE id = %s;'''
    cursor.execute(query, (question_id, ))
    delete_relevant_answers(question_id)


@database_common.connection_handler
def delete_relevant_answers(cursor, question_id):
    query = '''
        DELETE FROM answer
        WHERE question_id = %s;'''
    cursor.execute(query, (question_id, ))


@database_common.connection_handler
def voting(cursor, answer_id, vote):
    vote_change = 1 if vote == 'up' else -1
    query = '''
        UPDATE answer
        SET vote_number = vote_number + CAST(%s AS int)
        WHERE id = %s;'''
    cursor.execute(query, (vote_change, answer_id))
    # vote_number = int(database[data_index]['vote_number'])
    # vote_number += 1 if vote == 'up' else (-1 if vote == 'down' else 0)
    # database[data_index]['vote_number'] = vote_number
    # return database


@database_common.connection_handler
def get_related_question(cursor, answer_id):
    query = '''
        SELECT question_id
        FROM answer
        WHERE id = %s'''
    cursor.execute(query, (answer_id, ))
    return cursor.fetchone()


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
