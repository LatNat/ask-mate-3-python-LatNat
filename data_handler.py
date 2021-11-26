import csv
import os
import codecs

DATA_FILE_PATH_ANSWER = os.getenv('DATA_FILE_PATH_ANSWER') if 'DATA_FILE_PATH_ANSWER' in os.environ else 'answer.csv'
DATA_FILE_PATH_QUESTION = os.getenv('DATA_FILE_PATH_QUESTION') if 'DATA_FILE_PATH_QUESTION' in os.environ else 'question.csv'
DATA_HEADER_ANSWER = ["id", "submission_time", "vote_number", "question_id", "message", "image"]
DATA_HEADER_QUESTION = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]


def data_import(file_name):
    with open(file_name, encoding='utf-8') as file:
        lines = csv.DictReader(file)
        data = [x for x in lines]
    return data


def data_export(filename, dict_data, header):
    with open(filename, "w", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)


def get_list_index(dict_list, id):
    i = 0
    for line in dict_list:
        if line["id"] == id:
            return i
        i += 1
    return -1


def sort_data(data, key="submission_time", reverse=False):
    if not data:
        return data
    elif data[0][key].isnumeric():
        return sorted(data, key=lambda x: int(x[key]), reverse=reverse)
    else:
        return sorted(data, key=lambda x: x[key].lower(), reverse=reverse)


def voting(database, data_index, vote):
    vote_number = int(database[data_index]['vote_number'])
    vote_number += 1 if vote == 'up' else (-1 if vote == 'down' else 0)
    database[data_index]['vote_number'] = vote_number
    return database
    pass


def delete_pictures(question_id, folder):
    all_answers = data_import(DATA_FILE_PATH_ANSWER)
    to_delete = list(filter(lambda x: x['question_id'] == question_id, all_answers))
    print(to_delete)
    files = [f['image'] for f in to_delete]
    for file in files:
        try:
            os.remove(os.path.join(folder, file))
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    pass
