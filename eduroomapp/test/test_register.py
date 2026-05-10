import hashlib
import bcrypt
import pytest
from sqlalchemy.exc import IntegrityError
from eduroomapp import db
from eduroomapp.dao import add_user
from eduroomapp.models import UserRole, User
from eduroomapp.test.test_base import sample_rooms, test_app, test_session, sample_bookings, sample_users


def test_add_success(test_session, sample_users):
    add_user(fullname='Nguyen Dinh Nhat Truong',
             email='tn@gmail.com',
             username='gv01',
             password='345',
             user_role=UserRole.TEACHER)

    user = User.query.filter(User.username == 'gv01').first()
    assert user is not None
    assert user.username == 'gv01'
    assert bcrypt.checkpw("345".encode("utf-8"), user.password.encode("utf-8"))


def test_invalid_fullname(test_session):
    with pytest.raises(ValueError):
        add_user(fullname="Haha",
                 email="tn@gmail.com",
                 username="abc",
                 password="123",
                 user_role=UserRole.STUDENT)


@pytest.mark.parametrize('username, expected_message', [
    ('g1', "Username toi thieu 4 ky tu"),
    ('user2', "Username da ton tai")
])
def test_invalid_username(username, expected_message, test_session, sample_users):
    with pytest.raises(ValueError):
        add_user(fullname="Nhat Truong1",
                 email="tn@gmail.com",
                 username=username,
                 password="123",
                 user_role=UserRole.TEACHER)

@pytest.mark.parametrize('fullname, expected_message', [
    ('g1', "Fullname toi thieu 4 ky tu")
])
def test_invalid_fullname(fullname, expected_message, test_session, sample_users):
    with pytest.raises(ValueError):
        add_user(fullname=fullname,
                 email="tn@gmail.com",
                 username='jasdfkaksdfj',
                 password="123",
                 user_role=UserRole.TEACHER)

def test_invalid_password(test_session):
    with pytest.raises(ValueError):
        add_user(fullname="Nhat Truong2",
                 email="tn@gmail.com",
                 username="nhattruong2",
                 password="g1",
                 user_role=UserRole.STUDENT)


@pytest.mark.parametrize('email, expected_message', [
    ('u1@gmail.com', "Email da duoc dang ky"),
    ('tn@', "Email phai co duoi @gmail.com hoac dinh dang @ten_truong.edu.vn"),
    ('tn@.com', "Email phai co duoi @gmail.com hoac dinh dang @ten_truong.edu.vn"),
    ('tn@gmail.vn', "Email phai co duoi @gmail.com hoac dinh dang @ten_truong.edu.vn"),
    ('tn@ou.edu.com', "Email phai co duoi @gmail.com hoac dinh dang @ten_truong.edu.vn"),
    ('tn@ou.vn', "Email phai co duoi @gmail.com hoac dinh dang @ten_truong.edu.vn")
])
def test_invalid_email(email, expected_message, test_session, sample_users):
    with pytest.raises(ValueError):
        add_user(fullname="Nhat Truong2",
                 email=email,
                 username="nhattruong2",
                 password="123",
                 user_role=UserRole.STUDENT)


@pytest.mark.parametrize('fullname, username, password, email, expected_message', [
    ("     ", "admin1", "123", "tn@gmail.com", "Fullname toi thieu 4 ky tu"),
    ("Nguyen A", "    ", "123", "tn@gmail.com", "Username toi thieu 4 ky tu"),
    ("Nguyen A", "admin1", "   ", "tn@gmail.com", "Password toi thieu 3 ky tu"),
    ("Nguyen A", "admin1", "123", "        ", "Email phai co duoi @gmail.com hoac dinh dang @ten_truong.edu.vn")
])
def test_add_user_only_spaces_for_all_fields(fullname, username, password, email, expected_message, test_session):
    with pytest.raises(ValueError):
        add_user(
            fullname=fullname,
            username=username,
            password=password,
            user_role=UserRole.STUDENT,
            email=email
        )


def test_add_user_integrity_error(test_session, monkeypatch):
    def fake_commit_error():
        raise IntegrityError(None, None, None)

    monkeypatch.setattr(db.session, 'commit', fake_commit_error)

    with pytest.raises(Exception, match='Username đã tồn tại!'):
        add_user(
            fullname="Nguyen Van A",
            email="anguyen@gmail.com",
            username="nguyenvantuan123",
            password="123",
            user_role=UserRole.STUDENT
        )