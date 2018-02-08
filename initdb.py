from views import db, app
import models
with app.app_context():
    db.create_all()
