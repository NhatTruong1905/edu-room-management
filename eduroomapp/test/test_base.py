from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from eduroomapp import db, app as main_app
from eduroomapp.models import RoomStatus, Room, Booking, BookingStatus, User, UserRole
from eduroomapp.index import register_root


@pytest.fixture
def test_app():
    main_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    main_app.config["PAGE_SIZE"] = 2
    main_app.config["TESTING"] = True
    main_app.secret_key = '&(^&*^&*^U*HJBJKHJLHKJHK&*%^&5786985646858'

    if 'home' not in main_app.view_functions:
        register_root(app=main_app)
    if "sqlalchemy" not in main_app.extensions:
        db.init_app(main_app)

    with main_app.app_context():
        db.create_all()
        yield main_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.fixture
def sample_rooms(test_session):
    r1 = Room(name="A101", capacity=50, status=RoomStatus.AVAILABLE)
    r2 = Room(name="A102", capacity=100, status=RoomStatus.AVAILABLE)
    r3 = Room(name="A103", capacity=55, status=RoomStatus.AVAILABLE)
    r4 = Room(name="A104", capacity=20, status=RoomStatus.AVAILABLE)

    test_session.add_all([r1, r2, r3, r4])
    test_session.commit()
    return [r1, r2, r3, r4]


@pytest.fixture
def sample_users(test_session):
    u1 = User(fullname="Nguyen Dinh Nhat Truong", username="gv02", password="123", email="u1@gmail.com",
              user_role=UserRole.TEACHER)
    u2 = User(fullname="Nguyen Van Tuan", username="user2", password="123", email="u2@gmail.com",
              user_role=UserRole.STUDENT)

    test_session.add_all([u1, u2])
    test_session.commit()
    return [u1, u2]

@pytest.fixture
def sample_bookings(test_session, sample_rooms, sample_users):
    r1, r2, r3, r4 = sample_rooms
    u1, u2 = sample_users

    b1 = Booking(
        room_id=r1.id,
        user_id=u1.id,
        start_time=datetime(2026, 4, 20, 9, 0),
        end_time=datetime(2026, 4, 20, 11, 0),
        status=BookingStatus.CONFIRMED
    )

    b2 = Booking(
        room_id=r2.id,
        user_id=u1.id,
        start_time=datetime(2026, 4, 20, 9, 0),
        end_time=datetime(2026, 4, 20, 11, 0),
        status=BookingStatus.CANCELED
    )

    b3 = Booking(
        room_id=r3.id,
        user_id=u2.id,
        start_time=datetime(2026, 4, 20, 12, 10),
        end_time=datetime(2026, 4, 20, 17, 0),
        status=BookingStatus.CONFIRMED
    )

    b4 = Booking(
        room_id=r4.id,
        user_id=u2.id,
        start_time=datetime(2026, 5, 20, 15, 0),
        end_time=datetime(2026, 5, 20, 17, 0),
        status=BookingStatus.CONFIRMED
    )

    test_session.add_all([b1, b2, b3, b4])
    test_session.commit()
    return [b1, b2, b3, b4]


@pytest.fixture
def sample_admin(test_session):
    admin = User(fullname="Nguyen Van Tuan", username="admin", password="123", email="admin@gmail.com",
              user_role=UserRole.ADMIN)

    test_session.add(admin)
    test_session.commit()
    return admin

@pytest.fixture
def auth_client(test_client, mocker):
    class FakeUser:
        def __init__(self):
            self.id = 1
            self.locked_until = None
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False
            self.user_role = UserRole.TEACHER

        def get_id(self):
            return str(self.id)

    fake_user = FakeUser()
    mocker.patch('flask_login.utils._get_user', return_value=fake_user)
    return test_client, fake_user

