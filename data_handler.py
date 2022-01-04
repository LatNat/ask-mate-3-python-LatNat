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
    for row in get_related_comments("question_id", question_id):
        delete_comment_by_id(row['id'])
    query = '''
        DELETE FROM question
        WHERE id = %s;'''
    cursor.execute(query, (question_id, ))


@database_common.connection_handler
def delete_relevant_answers(cursor, question_id):
    for row in get_answers_by_question_id(question_id):
        delete_answer(row['id'])


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
    cursor.execute(query, (answer_id, ))
    return cursor.fetchone()


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    for row in get_related_comments("answer_id", answer_id):
        delete_comment_by_id(row['id'])
    query = '''
        DELETE FROM answer
        WHERE id = %s'''
    cursor.execute(query, (answer_id, ))


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
            LEFT JOIN answer ON answer.question_id = question.id
            WHERE question.id = %s;'''
    cursor.execute(query, (question_id, ))
    a = cursor.fetchall()
    for row in a:
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


@database_common.connection_handler
def add_comment(cursor, id_type, id_number, message):
    query = sql.SQL('''INSERT INTO comment ({id_type}, message, submission_time)
                VALUES ({id_number}, {message}, {submission_time});''')
    cursor.execute(query.format(
        id_type=sql.Identifier(id_type),
        id_number=sql.Literal(id_number),
        message=sql.Literal(message),
        submission_time=sql.Literal(round_seconds(dt.datetime.now()))
    ))


@database_common.connection_handler
def get_related_comments(cursor, id_type, id_number):
    query = sql.SQL('''SELECT * FROM comment
                    WHERE {id_type}={id_number};''')
    cursor.execute(query.format(
        id_type=sql.Identifier(id_type),
        id_number=sql.Literal(id_number),
    ))
    return cursor.fetchall()


@database_common.connection_handler
def delete_comment_by_id(cursor, comment_id):
    query = sql.SQL('''DELETE FROM comment
                        WHERE id={comment_id};''')
    cursor.execute(query.format(comment_id=sql.Literal(comment_id)))


@database_common.connection_handler
def update_comment(cursor, comment_id, message):
    query = sql.SQL('''UPDATE comment
                        SET message={message},
                         edited_count=(CASE WHEN edited_count IS NULL THEN 1 ELSE edited_count+1 END)
                        WHERE id={comment_id};''')
    cursor.execute(query.format(message=sql.Literal(message), comment_id=sql.Literal(comment_id)))


@database_common.connection_handler
def get_comment_message(cursor, id_number):
    query = sql.SQL('''SELECT * FROM comment
                    WHERE id={id_number};''')
    cursor.execute(query.format(id_number=sql.Literal(id_number)))
    return cursor.fetchone()["message"]


@database_common.connection_handler
def search_in_questions(cursor, search_term, order, asc_desc):
    if asc_desc:
        asc_desc = "asc"
    else:
        asc_desc = "desc"
    query = sql.SQL('''
                SELECT * FROM question
                LEFT JOIN
                    (SELECT DISTINCT question_id, string_agg(name, ',') as tag_name FROM tag
                    LEFT JOIN question_tag qt ON tag.id = qt.tag_id
                        GROUP BY qt.question_id) as tags
                        ON tags.question_id = question.id
                WHERE title ~* {search_term} OR message ~* {search_term} OR (CASE WHEN tag_name IS NULL THEN False ELSE tag_name ~* {search_term} END)
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
def get_first_five(cursor, order, asc_desc):
    asc_desc = "asc" if asc_desc else "desc"
    query = sql.SQL('''
            SELECT * FROM question
            ORDER BY {order_by} {asc_desc}
            LIMIT 5;''')
    cursor.execute(query.format(
        order_by=sql.Identifier(order),
        asc_desc=sql.SQL(asc_desc)))
    return cursor.fetchall()


@database_common.connection_handler
def delete_relevant_tags(cursor, question_id):
    query = '''
        DELETE FROM question_tag
        WHERE question_id = %s;
        '''
    cursor.execute(query, (question_id, ))


@database_common.connection_handler
def get_questions_by_tag(cursor, tag):
    query = '''
        SELECT * FROM question
        JOIN
            (SELECT question_id FROM question_tag
            JOIN tag
                ON question_tag.tag_id = tag.id
            WHERE tag.name = %s ) AS relevant_question_ids
            ON question.id = relevant_question_ids.question_id
        '''
    cursor.execute(query, (tag, ))
    return cursor.fetchall()


@database_common.connection_handler
def remove_tag_from_question(cursor, tag, question_id):
    query = '''
        DELETE FROM question_tag
        WHERE tag_id = %s AND question_id = %s'''
    cursor.execute(query, (tag, question_id))


@database_common.connection_handler
def remove_unused_tags(cursor):
    query = '''
        DELETE FROM tag
        WHERE id NOT IN (SELECT DISTINCT tag_id FROM question_tag)'''
    cursor.execute(query)


@database_common.connection_handler
def get_related_tags(cursor, question_id):
    query = '''
        SELECT name from tag
        JOIN question_tag qt on tag.id = qt.tag_id
        Where question_id = %s;'''
    cursor.execute(query, (question_id, ))
    return cursor.fetchall()


@database_common.connection_handler
def image_name_number_from_id(cursor):
    query = '''
            SELECT id from question
            ORDER BY id desc;'''
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def create_user(cursor, data):
    query = '''
                INSERT INTO users(name, password, registered, email, reputation)
                VALUES(%(name)s, %(password)s, %(registered)s, %(email)s, %(reputation)s);'''
    cursor.execute(query, {
        "name": data["name"],
        "password": data["password"],
        "registered": data["registered"],
        "email": data["email"],
        "reputation": data["reputation"]})


@database_common.connection_handler
def login_user(cursor, data):
    query = '''
                SELECT * FROM users
                WHERE email = %(username)s or name = %(username)s'''
    cursor.execute(query, {"username": data})
    return cursor.fetchone()


if __name__ == "__main__":
    pass
