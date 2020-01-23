from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = "c51317ef8101119798a6819d082bfb0c"

from server import routes # must be the last line in the document
