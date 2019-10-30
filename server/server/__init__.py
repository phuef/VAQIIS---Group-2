from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "c51317ef8101119798a6819d082bfb0c"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///airpolution.db"
db = SQLAlchemy(app)

from server import routes
