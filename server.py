from flask import Flask, request, render_template, redirect, url_for
import data_handler
from datetime import datetime
import time
import os
from werkzeug.utils import secure_filename

dirname = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(dirname, "static", "images")
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/list", methods=['GET', 'POST'])
@app.route("/", methods=["GET", "POST"])
def list_index():
    data = data_handler.import_all_questions()
    # if request.method == "POST":
    #     checked = False
    #     if "reverse" in request.form.keys():
    #         checked = True
    #     data = data_handler.sort_data(data, key=request.form["sort_key"], reverse=not checked)
    #     return render_template("index.html", data=data, default_sort=request.form["sort_key"], checked=checked)
    # else:
    #     data = data_handler.sort_data(data)
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    return render_template("index.html", data=data, default_sort="submission_time", checked=False, path=path)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def display_question(question_id):
    question = data_handler.get_question_by_id(question_id)
    relevant_answers = data_handler.get_answers_by_question_id(question_id)
    # question = next((q for q in all_questions if q["id"] == question_id), None)
    # question_index = all_questions.index(question)
    # if 'view' not in request.args:
    #     question["view_number"] = int(question["view_number"]) + 1
    # relevant_answers = [a for a in all_answers if a['question_id'] == str(question_id)]
    # relevant_answers = sorted(relevant_answers, key=lambda x: int(x["vote_number"]), reverse=True)
    # all_questions[question_index] = question
    # data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, all_questions, data_handler.DATA_HEADER_QUESTION)
    return render_template("question.html", question=question, answers=relevant_answers)


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "GET":
        line = data_handler.get_question_by_id(question_id)
        return render_template("addquestion.html", data=line, edit="edit")
    if request.method == "POST":
        update_data = {"id": question_id, "message": request.form["message"], "title": request.form["title"]}
        data_handler.update_question(update_data)
        return redirect(url_for("list_index"))
    # all_lines = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    # if request.method == "GET":
    #     line = next((q for q in all_lines if q["id"] == question_id), None)
    #     return render_template("addquestion.html", data=line, edit="edit")
    # if request.method == "POST":
    #     line_index = data_handler.get_list_index(all_lines, question_id)
    #     all_lines[line_index]["message"] = (request.form["message"])
    #     all_lines[line_index]["title"] = (request.form["title"])
    #     data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, all_lines, data_handler.DATA_HEADER_QUESTION)
    #     return redirect(url_for("list_index"))


@app.route("/addquestion", methods=["GET", "POST"])
def add_question():
    if request.method == "GET":
        return render_template("addquestion.html")
    if request.method == "POST":
        add_question_data = request.form.to_dict()
        data_handler.add_question(add_question_data)
        # data = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
        # new_id = int(data[-1]["id"])+1
        # filename = ""
        # if request.files:
        #     file = request.files["file"]
        #     filename = secure_filename(file.filename)
        #     if filename != "":
        #         file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        # new_question = {"id": new_id, "submission_time": int((datetime.now()).timestamp()),
        #                 "view_number": 0, "vote_number": 0,
        #                 "title": (request.form["title"]), "message": (request.form["message"]),
        #                 "image": (filename if filename != "" else "")}
        # data.append(new_question)
        # data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, data, data_handler.DATA_HEADER_QUESTION)
        return redirect(url_for("list_index"))


@app.route('/question/<question_id>/<vote>')
def vote_question(question_id, vote):
    all_questions = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    index = data_handler.get_list_index(all_questions, question_id)
    all_questions = data_handler.voting(all_questions, index, vote)
    data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, all_questions, data_handler.DATA_HEADER_QUESTION)
    return redirect(url_for('list_index'))


@app.route('/answer/<answer_id>/<vote>')
def vote_answer(answer_id, vote):
    answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    index = data_handler.get_list_index(answers, answer_id)
    answers = data_handler.voting(answers, index, vote)
    question_id = answers[index]['question_id']
    data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
    return redirect(url_for('display_question', question_id=question_id, view='f'))


@app.route("/answer/<question_id>", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "POST":
        filename = ""
        if request.files:
            file = request.files["image"]
            filename = secure_filename(file.filename)
            if filename != "":
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
        new_answer = {"id": str(max([int(row["id"]) for row in answers])+1), "submission_time": str(int(time.time())),
                      "vote_number": "0", "question_id": question_id, "message": request.form["answer_message"],
                      "image": (filename if filename != "" else "")}
        answers.append(new_answer)
        data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
        return redirect(url_for("display_question", question_id=question_id, view="f"))
    return render_template("addanswer.html", question_id=question_id)


@app.route("/answer/<question_id>/<answer_id>", methods=["GET", "POST"])
def update_answer(question_id, answer_id):
    answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    index = data_handler.get_list_index(answers, answer_id)
    if request.method == "POST":
        answers[index]["message"] = request.form["answer_message"]
        data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
        return redirect(url_for("display_question", question_id=question_id, view="f"))
    return render_template("editanswer.html", message=answers[index]["message"], question_id=question_id)


@app.route("/answer/delete/<question_id>/<answer_id>", methods=["GET", "POST"])
def delete_answer(question_id, answer_id):
    answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    index = data_handler.get_list_index(answers, answer_id)
    if answers[index]["image"] != "":
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, answers[index]["image"]))
        except FileNotFoundError:
            pass
    del answers[index]
    data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, answers, data_handler.DATA_HEADER_ANSWER)
    return redirect(url_for("display_question", question_id=question_id, view="f"))


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    # all_questions = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    # question_index = data_handler.get_list_index(all_questions, question_id)
    # if all_questions[question_index]["image"] != "":
    #     try:
    #         os.remove(os.path.join(UPLOAD_FOLDER, all_questions[question_index]["image"]))
    #     except FileNotFoundError:
    #         pass
    # del all_questions[question_index]
    # data_handler.delete_pictures(question_id, UPLOAD_FOLDER)
    # all_answers = data_handler.data_import(data_handler.DATA_FILE_PATH_ANSWER)
    # to_export = list(filter(lambda x: x['question_id'] != question_id, all_answers))
    # data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION, all_questions, data_handler.DATA_HEADER_QUESTION)
    # data_handler.data_export(data_handler.DATA_FILE_PATH_ANSWER, to_export, data_handler.DATA_HEADER_ANSWER)
    return redirect(url_for("list_index"))


@app.route("/result", methods=["GET","POST"])
def search():
    all_question = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    search_term = request.args["search"].upper()
    relevant_questions = [q for q in all_question if search_term in q["title"].upper() or search_term in q["message"].upper()]
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    relevant_questions = data_handler.sort_data(relevant_questions, key="vote_number", reverse=True)
    if request.method == "POST":
        checked = False
        if "reverse" in request.form.keys():
            checked = True
        data = data_handler.sort_data(relevant_questions, key=request.form["sort_key"], reverse=checked)
        return render_template("index.html", data=data, default_sort=request.form["sort_key"], checked=checked)
    return render_template("index.html", data=relevant_questions, default_sort="vote_number", checked=False, path=path)


if __name__ == "__main__":
    app.run(debug=True)
