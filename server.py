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


@app.route("/question/<question_id>")
def display_question(question_id):
    all_questions = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    question = next((q for q in all_questions if q["id"] == question_id), None)
    question_index = all_questions.index(question)
    all_answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    question["view_number"] = int(question["view_number"]) + 1
    relevant_answers = [a for a in all_answers if a['question_id'] == str(question_id)]
    relevant_answers = sorted(relevant_answers, key=lambda x: x["submission_time"])
    all_questions[question_index] = question
    data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, all_questions, data_handler.DATA_HEADER_QUESTION)
    return render_template("question.html", question=question, answers=relevant_answers)


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    all_lines = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    if request.method == "GET":
        line = next((q for q in all_lines if q["id"] == question_id), None)
        return render_template("addquestion.html", data=line, edit="edit")
    if request.method == "POST":
        line_index = data_handler.get_list_index(data_handler.DATA_FILE_PATH_QUESTION, question_id)
        all_lines[line_index]["message"] = (request.form["message"])
        all_lines[line_index]["title"] = (request.form["title"])
        data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION,all_lines,data_handler.DATA_HEADER_QUESTION)
        return redirect(url_for("list_index"))


@app.route("/addquestion", methods=["GET", "POST"])
def add_question():
    if request.method == "GET":
        return render_template("addquestion.html")
    if request.method == "POST":
        data = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
        new_id = int(data[-1]["id"])+1
        if request.form['file']:
            pass
            # uploaded = request.files["file"]
            # uploaded.save("/images")
        new_question = {"id": new_id,
                        "submission_time": int((datetime.now()).timestamp()),
                        "view_number": 0,
                        "vote_number": 0,
                        "title": (request.form["title"]),
                        "message": (request.form["message"]),
                        "image": ""}
        data.append(new_question)
        data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, data, data_handler.DATA_HEADER_QUESTION)
        return redirect(url_for("list_index"))


@app.route('/answer/<answer_id>/vote_up')
def vote_up(answer_id):
    pass


@app.route('/answer/<answer_id>/vote_down')
def vote_down(answer_id):
    pass


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
        redirect(url_for("display_question", question_id=question_id))
    return render_template("addanswer.html")


@app.route("/answer/<question_id>/<id>", methods=["GET", "POST"])
def update_answer(question_id, id):
    if request.method == "POST":
        answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
        index = data_handler.get_list_index(answers, id)
        answers[index]["message"] = request.form["message"]
        data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
        redirect(url_for("display_question", question_id=question_id))
    return render_template("editanswer.html")


if __name__ == "__main__":
    app.run(debug=True)
