from flask import redirect, render_template, request, url_for
from server import app

from .cluster_data import main
import pickle
import os


@app.route("/")
@app.route("/map")
def index():
    return render_template("index.html")

# @app.route("/getroi_level/<int:time>/<int:level>", methods=["GET"])
# def getroi_level(level:int):
#     levels = pickle.load(open(os.path.join("server", "data_folder", "rois.p"), "rb"))
#     return {"status": "OK", "data": levels[level]}

@app.route("/getrois", methods=["GET"])
def getrois():
    try:
        levels = pickle.load(open(os.path.join("server", "data_folder", "rois.p"), "rb"))
        return {"status": "OK", "data": levels}
    except FileNotFoundError:
        return {"status": "OK", "data": []}

@app.route("/upload", methods=["GET"])
def upload():
    return render_template("upload.html")

@app.route("/api/upload", methods=["POST"])
def api_upload():
    new_file = request.files["fileUpload"]
    main(new_file)
    return redirect("/")

    
