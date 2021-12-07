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
def import_all_questions(cursor, order, asc_desc=False):
    if asc_desc:
        asc_desc = "asc"
    else:
        asc_desc = "desc"
    query = sql.SQL('''
        SELECT * FROM question
        ORDER BY {order_by} {asc_desc};''')
    cursor.execute(query.format(
        order_by=sql.Identifier(order),
        asc_desc=sql.SQL(asc_desc)))
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
    delete_relevant_answers(question_id)
    query = '''
        DELETE FROM question
        WHERE id = %s;'''
    cursor.execute(query, (question_id, ))


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


@database_common.connection_handler
def delete_picture_by_answer_id(cursor, answer_id, folder):
    query = '''
            SELECT image FROM answer
            WHERE id = %s;'''
    cursor.execute(query, (answer_id,))
    delete_picture(cursor.fetchone()["image"], folder)


@database_common.connection_handler
def delete_pictures_by_question_id(cursor, question_id, folder):
    query = '''
            SELECT answer.image as answer_image, question.image as question_image
            FROM question
            JOIN answer ON answer.question_id = question.id
            WHERE question.id = %s;'''
    cursor.execute(query, (question_id, ))
    for row in cursor.fetchall():
        delete_picture(row["answer_image"], folder)
        delete_picture(row["question_image"], folder)


@database_common.connection_handler
def get_latest_id(cursor):
    query = '''
        SELECT MAX(id) FROM question'''
    cursor.execute(query)
    return cursor.fetchone()


def delete_picture(filename, folder):
    if filename:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        os.remove(os.path.join(folder, filename))


@database_common.connection_handler
def search_in_questions(cursor, search_term, order, asc_desc):
    if asc_desc:
        asc_desc = "asc"
    else:
        asc_desc = "desc"
    query = sql.SQL('''
                SELECT * FROM question
                WHERE title ~* {search_term} OR message ~* {search_term}
                ORDER BY {order_by} {asc_desc};''')
    cursor.execute(query.format(search_term=sql.Literal("\y"+search_term.lower()+"\y"),
                                order_by=sql.Identifier(order),
                                asc_desc=sql.SQL(asc_desc)))
    return cursor.fetchall()


@database_common.connection_handler
def convert_tag(cursor, tag_to_convert):
    query = '''
        SELECT id FROM tag
        WHERE name = %s'''
    cursor.execute(query, (tag_to_convert, ))
    return cursor.fetchone()


@database_common.connection_handler
def get_all_tags(cursor):
    query = '''
        SELECT DISTINCT name FROM tag'''
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def create_new_tag(cursor, tag):
    query = '''
        INSERT INTO tag(name)
        VALUES (%s)
    '''
    cursor.execute(query, (tag, ))


@database_common.connection_handler
def add_tag_to_question(cursor, question_id, tag):
    query = '''
        INSERT INTO question_tag(question_id, tag_id) 
        VALUES (%s, %s)
        '''
    cursor.execute(query, (question_id, tag))


@database_common.connection_handler
def delete_relevant_tags(cursor, question_id):
    query = '''
        DELETE FROM question_tag
        WHERE question_id = %s;
        '''
    cursor.execute(query, (question_id, ))


@database_common.connection_handler
def get_first_five(cursor, order, asc_desc):
    asc_desc = "desc" if asc_desc else "asc"
    query = sql.SQL('''
            SELECT * FROM question
            ORDER BY {order_by} {asc_desc}
            LIMIT 5;''')
    cursor.execute(query.format(
        order_by=sql.Identifier(order),
        asc_desc=sql.SQL(asc_desc)))
    return cursor.fetchall()


if __name__ == "__main__":
    pass
