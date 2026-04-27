from eduroomapp import app
from eduroomapp.index import register_root

register_root(app)

if __name__ == "__main__":
    app.run()
