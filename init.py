from flask import Flask
import config
from models import db

app = Flask(__name__)

if config.DEBUG:
    print("Running in DEBUG")
    app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///templates.db'
app.secret_key = "mhx2PDJk"
db.init_app(app)

