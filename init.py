from flask import Flask
import config

app = Flask(__name__)

if config.DEBUG:
    print("Running in DEBUG")
    app.debug = True

app.secret_key = ""

