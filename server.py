from flask import Flask, request, render_template, redirect, url_for
import data_handler
import datetime as dt
import os
from werkzeug.utils import secure_filename

dirname = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(dirname, "static", "images")
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/list", methods=['GET', 'POST'])
@app.route("/", methods=["GET", "POST"])
def list_index():
    data = []
    if request.method == "GET":
        data = data_handler.import_all_questions("submission_time")
    elif request.method == "POST":
        data = data_handler.import_all_questions(request.form["sort_key"])
        path = os.path.join(app.config['UPLOAD_FOLDER'])
        return render_template("index.html", data=data, default_sort=request.form["sort_key"], checked=False, path=path)
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
    if 'view' not in request.args:
        data_handler.increment_views(question_id)
    tags = data_handler.get_tags(question_id)
    question = data_handler.get_question_by_id(question_id)
    relevant_answers = data_handler.get_answers_by_question_id(question_id)
    return render_template("question.html", question=question, tags=tags, answers=relevant_answers)


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
        filename = ""
        if request.files:
            file = request.files["file"]
            filename = secure_filename(file.filename)
            if filename != "":
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        add_question_data["image"] = (filename if filename != "" else "")
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


@app.route('/question/vote/<question_id>/<vote>')
def vote_question(question_id, vote):
    data_handler.vote_for_question(question_id, vote)
    return redirect(url_for('list_index'))


@app.route('/answer/vote/<answer_id>/<vote>')
def vote_answer(answer_id, vote):
    data_handler.vote_for_answer(answer_id, vote)
    question_id = data_handler.get_related_question(answer_id)['question_id']
    return redirect(url_for('display_question', question_id=question_id, view='f'))


@app.route("/answer/<question_id>", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "POST":
        new_answer = {"submission_time": data_handler.round_seconds(dt.datetime.now()),
                      "vote_number": "0", "question_id": question_id, "message": request.form["answer_message"]}
        if request.files["image"]:
            file = request.files["image"]
            new_answer["image"] = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_answer["image"]))
        data_handler.add_answer(new_answer)
        return redirect(url_for("display_question", question_id=question_id, view="f"))
    return render_template("addanswer.html", question_id=question_id)


@app.route("/answer/<question_id>/<answer_id>", methods=["GET", "POST"])
def update_answer(question_id, answer_id):
    old_message = data_handler.get_answer_message(answer_id)['message']
    if request.method == "POST":
        data_handler.update_answer(request.form["answer_message"], answer_id)
        return redirect(url_for("display_question", question_id=question_id, view="f"))
    return render_template("editanswer.html", message=old_message, question_id=question_id)


@app.route("/answer/delete/<question_id>/<answer_id>", methods=["GET", "POST"])
def delete_answer(question_id, answer_id):
    data_handler.delete_picture_by_answer_id(answer_id, UPLOAD_FOLDER)
    data_handler.delete_answer(answer_id)
    return redirect(url_for("display_question", question_id=question_id, view="f"))


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    data_handler.delete_question(question_id)
    data_handler.delete_relevant_answers(question_id)
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
