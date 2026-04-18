from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 6

db = SQLAlchemy(app=app)
login = LoginManager(app=app)
