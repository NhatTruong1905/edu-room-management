from eduroomapp import app, db
from eduroomapp.index import register_root
from eduroomapp.models import add_data

register_root(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    from eduroomapp.models import User

    if not User.query.filter_by(username='admin1').first():
        add_data()

application = app

if __name__ == "__main__":
    app.run()
