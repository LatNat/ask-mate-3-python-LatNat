import csv
import os

DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'answer.csv'
# DATA_FILE_PATH = "sample_data/answer.csv"


def data_import(file_name, separator=","):
    with open(file_name) as file:
        lines = csv.DictReader(file)
        data = [x for x in lines]
    return data


print(data_import(DATA_FILE_PATH))
