import hashlib
import re

from sqlalchemy.exc import IntegrityError

from eduroomapp import db
from eduroomapp.models import User


def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()


def add_user(fullname, username, password):
    if User.query.filter(User.username == username).first():
        raise ValueError("Username đã tồn tại")

    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(fullname=fullname.strip(), username=username.strip(), password=password)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Username đã tồn tại!')
