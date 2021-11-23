from flask import Flask, request, render_template, redirect, url_for

import data_handler
from datetime import datetime
import time
import os

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def list_index():
    data = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    if request.method == "POST":
        checked = False
        if "reverse" in request.form.keys():
            checked = True
        data = data_handler.sort_data(data, key=request.form["sort_key"], reverse=checked)
        return render_template("index.html", data=data, default_sort=request.form["sort_key"], checked=checked)
    else:
        data = data_handler.sort_data(data)
        return render_template("index.html", data=data, default_sort="submission_time", checked=False)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def display_question(question_id):
    all_questions = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    question = next((q for q in all_questions if q["id"] == question_id), None)
    question_index = all_questions.index(question)
    all_answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    if 'view' not in request.args:
        question["view_number"] = int(question["view_number"]) + 1
    relevant_answers = [a for a in all_answers if a['question_id'] == str(question_id)]
    relevant_answers = sorted(relevant_answers, key=lambda x: x["vote_number"], reverse=True)
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
        filename = ""
        if request.form['file']:
            # filename = request.form["file"]
            # file = request.file["file"]
            # file.save(os.path.join(app.config["/images/"], filename))
            # return redirect(url_for('download_file', name=filename))
            pass
        new_question = {"id": new_id,
                        "submission_time": int((datetime.now()).timestamp()),
                        "view_number": 0,
                        "vote_number": 0,
                        "title": (request.form["title"]),
                        "message": (request.form["message"]),
                        "image": (f"/images/{filename}" if filename != "" else "")}
        data.append(new_question)
        data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, data, data_handler.DATA_HEADER_QUESTION)
        return redirect(url_for("list_index"))


@app.route('/question/<question_id>/vote_up')
def vote_up_question(question_id):
    all_questions = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    index = data_handler.get_list_index(all_questions, question_id)
    vote_number = int(all_questions[index]['vote_number'])
    vote_number += 1
    all_questions[index]['vote_number'] = vote_number
    data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, all_questions, data_handler.DATA_HEADER_QUESTION)
    return redirect(url_for('list_index'))


@app.route('/question/<question_id>/vote_down')
def vote_down_question(question_id):
    all_questions = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    index = data_handler.get_list_index(all_questions, question_id)
    vote_number = int(all_questions[index]['vote_number'])
    vote_number -= 1
    all_questions[index]['vote_number'] = vote_number
    data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, all_questions, data_handler.DATA_HEADER_QUESTION)
    return redirect(url_for('list_index'))


@app.route('/answer/<answer_id>/vote_up')
def vote_up_answer(answer_id):
    answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    index = data_handler.get_list_index(answers, answer_id)
    vote_number = int(answers[index]['vote_number'])
    vote_number += 1
    answers[index]['vote_number'] = vote_number
    question_id = answers[index]['question_id']
    data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
    return redirect(url_for('display_question', question_id=question_id, view='f'))


@app.route('/answer/<answer_id>/vote_down')
def vote_down_answer(answer_id):
    answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    index = data_handler.get_list_index(answers, answer_id)
    vote_number = int(answers[index]['vote_number'])
    if vote_number > 0:
        vote_number -= 1
        answers[index]['vote_number'] = vote_number
    else:
        pass
    question_id = answers[index]['question_id']
    data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
    return redirect(url_for('display_question', question_id=question_id, view='f'))


@app.template_filter("convert_timestamp")
def convert_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp))


@app.route("/answer/<question_id>", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "POST":
        new_answer={}
        answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
        new_answer["id"] = str(max([int(row["id"]) for row in answers])+1)
        new_answer["submission_time"] = str(int(time.time()))
        new_answer["vote_number"] = "0"
        new_answer["question_id"] = question_id
        new_answer["message"] = request.form["answer_message"]
        new_answer["image"] = ""
        answers.append(new_answer)
        data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
        return redirect(url_for("display_question", question_id=question_id))
    return render_template("addanswer.html")


@app.route("/answer/<question_id>/<id>", methods=["GET", "POST"])
def update_answer(question_id, id):
    answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    index = data_handler.get_list_index(answers, id)
    if request.method == "POST":
        answers[index]["message"] = request.form["message"]
        data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
        return redirect(url_for("display_question", question_id=question_id))
    return render_template("editanswer.html", message=answers[index]["message"])


@app.route("/answer/<question_id>/<id>", methods=["GET", "POST"])
def delete_answer(question_id, id):
    answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    index = data_handler.get_list_index(answers, id)
    del answers[id]
    data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
    return redirect(url_for("display_question", question_id=question_id))


if __name__ == "__main__":
    app.run(debug=True)
