from flask import Flask, request, render_template, redirect, url_for, session
import data_handler
import datetime as dt
import os
from werkzeug.utils import secure_filename

dirname = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(dirname, "static", "images")
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# cookies
app.secret_key = "any random string"


@app.before_first_request
def session_init():
    session.clear()
    session["sort"] = "submission_time"
    session["check"] = False


@app.template_filter()
def get_comments(id_type, id_number):
    return data_handler.get_related_comments(id_type, id_number)


@app.route("/", methods=["GET", "POST"])
def first_page():
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    if request.method == "GET":
        data = data_handler.get_first_five(session["sort"], session["check"])
        return render_template("index.html", data=data, default_sort=session["sort"], checked=session["check"], path=path)
    if request.method == "POST":
        session["sort"] = request.form["sort_key"]
        session["check"] = False
        if "reverse" in request.form.keys():
            session["check"] = True
        data = data_handler.get_first_five(session["sort"], session["check"])
        return render_template("index.html", data=data, default_sort=session["sort"], checked=session["check"], path=path)


@app.route("/list", methods=['GET', 'POST'])
def list_index():
    if request.method == "GET":
        data = data_handler.import_all_questions(session["sort"], session["check"])
    elif request.method == "POST":
        session["sort"] = request.form["sort_key"]
        session["check"] = False
        if "reverse" in request.form.keys():
            session["check"] = True
        data = data_handler.import_all_questions(request.form["sort_key"], session["checked"])
        path = os.path.join(app.config['UPLOAD_FOLDER'])
        return render_template("index.html", data=data, default_sort=session["sort"], checked=session["check"], path=path)
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    return render_template("index.html", data=data, default_sort=session["sort"], checked=session["check"], path=path)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def display_question(question_id):
    if 'view' not in request.args:
        data_handler.increment_views(question_id)
    question = data_handler.get_question_by_id(question_id)
    question_tags = data_handler.get_related_tags(question_id)
    relevant_answers = data_handler.get_answers_by_question_id(question_id)
    return render_template("question.html", question=question, tags=question_tags, answers=relevant_answers)


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    question = data_handler.get_question_by_id(question_id)
    question_tags = data_handler.get_related_tags(question_id)
    if request.method == "POST":
        update_data = {"id": question_id, "message": request.form["message"], "title": request.form["title"]}
        data_handler.update_question(update_data)
        old_tags = [dict(row)['name'] for row in question_tags]
        new_tags = [tag.strip() for tag in request.form["tags"].split(',') if tag.strip() != '']
        all_tags = [dict(row)['name'] for row in data_handler.get_all_tags()]
        converted_tags = []
        for tag in new_tags:
            if tag not in set(old_tags + all_tags):
                data_handler.create_new_tag(tag)
                converted_tags.append((data_handler.convert_tag(tag)["id"]))
            else:
                converted_tags.append((data_handler.convert_tag(tag)["id"]))
        if converted_tags:
            for tag in converted_tags:
                data_handler.add_tag_to_question(question_id, tag)
        return redirect(url_for("display_question", question_id=question_id))
    return render_template("addquestion.html", data=question, tags=question_tags, edit="edit")


@app.route("/addquestion", methods=["GET", "POST"])
def add_question():
    if request.method == "GET":
        return render_template("addquestion.html")
    if request.method == "POST":
        add_question_data = request.form.to_dict()
        filename = None
        if request.files["file"]:
            file = request.files["file"]
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        add_question_data["image"] = filename
        data_handler.add_question(add_question_data)
        question_id = data_handler.get_latest_id()["max"]
        user_tags = [tag.strip() for tag in request.form["tags"].split(',')]
        all_tags = [dict(row)['name'] for row in data_handler.get_all_tags()]
        converted_tags = []
        if user_tags:
            for name in user_tags:
                if name not in all_tags:
                    data_handler.create_new_tag(name)
                    converted_tags.append((data_handler.convert_tag(name)['id']))
                else:
                    converted_tags.append((data_handler.convert_tag(name)['id']))
            if converted_tags:
                for tag in converted_tags:
                    data_handler.add_tag_to_question(question_id, tag)
        return redirect(url_for("list_index"))


@app.route('/question/vote/<question_id>/<vote>')
def vote_question(question_id, vote):
    data_handler.vote_for_question(question_id, vote)
    return redirect(url_for('first_page'))


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
    data_handler.delete_pictures_by_question_id(question_id, UPLOAD_FOLDER)
    data_handler.delete_relevant_tags(question_id)
    data_handler.delete_question(question_id)
    return redirect(url_for("list_index"))


@app.route("/result", methods=["GET", "POST"])
def search():
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    if request.method == "POST":
        checked = False
        if "reverse" in request.form.keys():
            checked = True
        data = data_handler.import_all_questions(request.args["search"], request.form["sort_key"], checked)
        return render_template("index.html", data=data, default_sort=request.form["sort_key"], checked=checked)
    search_result = data_handler.search_in_questions(request.args["search"], "submission_time", True)
    # if search_result:
    #     if request.args["search"].lower() in search_result[0]["title"].lower():
    #         bolding = search_result[0]["title"].lower().replace(request.args["search"], '<span style="color:red">' + request.args["search"] + '</span>')
    #         search_result[0]["title"] = bolding
        # if request.args["search"] in search_result[0]["message"]:
        #     bolding = search_result[0]["message"].replace(request.args["search"], '<span style="color:red;font-weight:bold">' + request.args["search"] + '</span>', search_result[0]["message"].count(request.args["search"]))
        #     search_result[0]["message"] = bolding
    return render_template("index.html", data=search_result, default_sort="vote_number", checked=False, path=path)


@app.route("/tagged/<tag>")
def get_tagged_questions(tag):
    tagged_questions = data_handler.get_questions_by_tag(tag)
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    return render_template("index.html", data=tagged_questions, default_sort="submission_time", checked=False, path=path)


@app.route("/answer/<answer_id>/comment", methods=["GET", "POST"])
def add_comment_to_answer(answer_id):
    question_id = data_handler.get_related_question(answer_id)["question_id"]
    if request.method == "POST":
        data_handler.add_comment("answer_id", answer_id, request.form["message"])
        return redirect(url_for("display_question", question_id=question_id))
    return render_template("addcomment.html", question_id=question_id)


@app.route("/question/<question_id>/comment", methods=["GET", "POST"])
def add_comment_to_question(question_id):
    if request.method == "POST":
        data_handler.add_comment("question_id", question_id, request.form["message"])
        return redirect(url_for("display_question", question_id=question_id))
    return render_template("addcomment.html", question_id=question_id)


@app.route("/comment/delete/<comment_id>/<question_id>", methods=["GET", "POST"])
def delete_comment(comment_id, question_id):
    data_handler.delete_comment_by_id(comment_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/comment/edit/<comment_id>/<question_id>", methods=["GET", "POST"])
def update_comment(comment_id, question_id):
    message = data_handler.get_comment_message(comment_id)
    if request.method == "POST":
        data_handler.update_comment(comment_id, request.form["message"])
        return redirect(url_for("display_question", question_id=question_id))
    return render_template("editcomment.html", question_id=question_id, message=message)


@app.route("/question/<question_id>/delete/<tag_name>")
def delete_tag(question_id, tag_name):
    question_id = question_id
    tag_id = data_handler.convert_tag(tag_name)["id"]
    data_handler.remove_tag_from_question(tag_id, question_id)
    data_handler.remove_unused_tags()
    return redirect(url_for('edit_question', question_id=question_id))


if __name__ == "__main__":
    app.run(debug=True)
