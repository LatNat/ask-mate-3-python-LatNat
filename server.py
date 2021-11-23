from flask import Flask, request, render_template, redirect, url_for

import data_handler
from datetime import datetime

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


if __name__ == "__main__":
    app.run(debug=True)
