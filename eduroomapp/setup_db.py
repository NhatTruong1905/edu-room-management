from eduroomapp import app, db
from eduroomapp.models import add_data

if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        add_data()
