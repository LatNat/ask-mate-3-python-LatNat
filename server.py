from flask import Flask, request, render_template, redirect, url_for

import data_handler
from datetime import datetime
import time

app = Flask(__name__)


@app.route("/")
def list_index():
    data = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    data = sorted(data, key=lambda x: x["submission_time"])
    return render_template("index.html", data=data)


@app.route("/addquestion")
def add_question():
    return render_template("addquestion.html")


@app.template_filter("convert_timestamp")
def convert_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp))


@app.route("/answer/<question_id>", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "POST":
        answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
        request.form["id"] = str(max([int(row["id"]) for row in answers])+1)
        request.form["submission_time"] = str(int(time.time()))
        request.form["vote_number"] = "0"
        request.form["question_id"] = question_id
        answers.append(request.form)
        data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
        redirect(url_for(""))
    return render_template("addanswer.html")


if __name__ == "__main__":
    app.run(debug=True)
