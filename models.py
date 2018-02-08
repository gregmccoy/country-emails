from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Template(db.Model):
    session = db.Column(db.String(100), unique=True, primary_key=True)
    html = db.Column(db.Text())
    country = db.Column(db.String(50))
    source = db.Column(db.String(50))
    result_notes = db.Column(db.Text())
    result_images = db.Column(db.Text())
    result_links = db.Column(db.Text())
    result_source = db.Column(db.Text())


    def __init__(self, session):
        self.session = session
        self.html = ""
        self.country =  ""
        self.source = ""
        self.result_notes = ""
        self.result_images = ""
        self.result_links = ""
        self.result_source = ""
