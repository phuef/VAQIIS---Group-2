from flask import redirect, render_template, url_for, request
from server import app
from .model import Airpolution
import json


@app.route("/")
def index():
	pass


@app.route("/add", methods=["POST"])
def add():
	pass


@app.route("/get_all")
def get_all():
	a = Airpolution.query.all()
	print(a)
	data = {"status": "OK", "data":[]}
	for point in a:
		data["data"].append({
			"id": point.id,
			"coordinates": [point.latitude, point.longitude],
			"data": point.data,
			"city": point.city,
			"street": point.street
		})
	return json.dumps(data)
