from eduroomapp import db, app
from eduroomapp.models import add_data

with app.app_context():
    db.create_all()
    add_data()