import csv
import os
import database_common
import datetime as dt
from psycopg2 import sql


def round_seconds(obj: dt.datetime) -> dt.datetime:
    if obj.microsecond >= 500_000:
        obj += dt.timedelta(seconds=1)
    return obj.replace(microsecond=0)


@database_common.connection_handler
def import_all_questions(cursor, order):
    query = sql.SQL('''
        SELECT * FROM question
        ORDER BY {order_by};''')
    cursor.execute(query.format(order_by=sql.Identifier(order)))
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
            VALUES(%(subtime)s, %(view)s, %(vote)s, %(title)s, %(message)s, %(image)s);'''
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
            WHERE id = %(id)s;'''
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
def add_answer(cursor, answer_dict):
    placeholder = ', '.join(['%s'] * len(answer_dict))
    columns = ', '.join(answer_dict.keys())
    query = '''
        INSERT INTO answer (%s)
        VALUES (%s);''' % (columns, placeholder)
    cursor.execute(query, list(answer_dict.values()))


@database_common.connection_handler
def update_answer(cursor, new_message, answer_id):
    query = '''
        UPDATE answer
        SET message = %s
        WHERE id = %s'''
    cursor.execute(query, (new_message, answer_id))


@database_common.connection_handler
def get_answer_message(cursor, answer_id):
    query = '''
        SELECT message FROM answer
        WHERE id = %s'''
    cursor.execute(query, answer_id)
    return cursor.fetchone()


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    query = '''
        DELETE FROM answer
        WHERE id = %s'''
    cursor.execute(query, answer_id)


@database_common.connection_handler
def vote_for_answer(cursor, answer_id, vote):
    vote_change = 1 if vote == 'up' else -1
    query = '''
        UPDATE answer
        SET vote_number = vote_number + CAST(%s AS int)
        WHERE id = %s;'''
    cursor.execute(query, (vote_change, answer_id))


@database_common.connection_handler
def vote_for_question(cursor, question_id, vote):
    vote_change = 1 if vote == 'up' else -1
    query = '''
        UPDATE question
        SET vote_number = vote_number + CAST(%s AS int)
        WHERE id = %s;'''
    cursor.execute(query, (vote_change, question_id))


@database_common.connection_handler
def get_related_question(cursor, answer_id):
    query = '''
        SELECT question_id
        FROM answer
        WHERE id = %s;'''
    cursor.execute(query, (answer_id, ))
    return cursor.fetchone()


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    query = '''
        DELETE FROM answer
        WHERE id = %s;'''
    cursor.execute(query, (answer_id, ))


@database_common.connection_handler
def increment_views(cursor, question_id):
    query = '''
        UPDATE question
        SET view_number = view_number + 1
        WHERE id = %s;'''
    cursor.execute(query, (question_id, ))


@database_common.connection_handler
def get_tags(cursor, question_id):
    query = '''
        SELECT name FROM tag
        LEFT JOIN question_tag
            ON tag.id = question_tag.tag_id
        WHERE question_id = %s;'''
    cursor.execute(query, (question_id, ))
    return cursor.fetchall()


if __name__ == "__main__":
    pass
