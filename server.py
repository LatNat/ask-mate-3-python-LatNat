from flask import Flask, request, render_template, redirect, url_for

import data_handler
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def list_index():
    data = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
    data = sorted(data, key=lambda x: x["submission_time"])
    return render_template("index.html", data=data)


@app.route("/addquestion", methods=["GET", "POST"])
def add_question():
    if request.method == "GET":
        return render_template("addquestion.html")
    if request.method == "POST":
        data = data_handler.data_import(data_handler.DATA_FILE_PATH_QUESTION)
        new_id = int(data[-1]["id"])+1  #globális változó?
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            uploaded_file.save(uploaded_file.filename)
        new_question = {"id": new_id,
                        "submission_time": datetime.now(),
                        "view_number": 0,
                        "vote_number": 0,
                        "title": (request.form["title"]),
                        "message": (request.form["text"]),
                        "image": (request.form["image"])}
        data.append(new_question)
        data_handler.data_export(data_handler.DATA_FILE_PATH_QUESTION_QUESTION, data, data_handler.DATA_HEADER_QUESTION)
        return redirect(url_for("list_index"))


@app.template_filter("convert_timestamp")
def convert_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp))


if __name__ == "__main__":
    app.run(debug=True)
