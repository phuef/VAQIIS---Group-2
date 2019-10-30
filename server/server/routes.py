from flask import redirect, render_template, url_for, request 
from server import app
from .model import Airpolution

@app.route('/')
def index():
	pass


@app.route('/add', methods=["POST"])
def add():
	pass


@app.route('/search')
def search():
	pass