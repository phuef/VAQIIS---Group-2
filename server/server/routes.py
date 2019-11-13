import json

from flask import redirect, render_template, request, url_for

from server import app, db

from .model import Airpolution
from .tools import model_to_json, log_data_to_file


@app.route("/")
def index():
    return "Hello"


@app.route("/add_to_database", methods=["POST"])
def add_to_database():
    data_point = Airpolution(
        longitude=7.87345867, latitude=51.834568, data=0.5, city="Muster", street="city"
    )
    db.session.add(data_point)
    db.session.commit()
    print(data_point)
    return {"status": "OK", "data": [model_to_json(data_point)]}


@app.route("/add_logger_line", methods=["POST"])
def add_logger_line():
    line = request.form['data']
    log_data_to_file(line)


@app.route("/get_all")
def get_all():
    a = Airpolution.query.all()
    print(a)
    data = {"status": "OK", "data": []}
    for point in a:
        data["data"].append(model_to_json(point))
    return data


@app.route("/get/<int:id>")
def get(id: int):
    a = Airpolution.query.filter_by(id=id)
    print(a)
    data = {"status": "OK", "data": []}
    for point in a:
        data["data"].append(model_to_json(point))
    return data
