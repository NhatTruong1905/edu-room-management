from datetime import datetime
import pytest
from flask import Flask
from eduroomapp import db
from eduroomapp.models import RoomStatus, Room, Booking, BookingStatus


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["PAGE_SIZE"] = 2
    app.config["TESTING"] = True
    app.secret_key = '&(^&*^&*^U*HJBJKHJLHKJHK&*%^&5786985646858'
    db.init_app(app)

    from eduroomapp.index import register_root
    register_root(app=app)

    return app


@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()


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
def sample_bookings(test_session, sample_rooms):
    r1, r2, r3, r4 = sample_rooms

    b1 = Booking(
        room_id=r1.id,
        start_time=datetime(2026, 4, 20, 9, 0),
        end_time=datetime(2026, 4, 20, 11, 0),
        status=BookingStatus.CONFIRMED
    )

    b2 = Booking(
        room_id=r2.id,
        start_time=datetime(2026, 4, 20, 9, 0),
        end_time=datetime(2026, 4, 20, 11, 0),
        status=BookingStatus.CANCELED
    )

    b3 = Booking(
        room_id=r3.id,
        start_time=datetime(2026, 4, 20, 15, 0),
        end_time=datetime(2026, 4, 20, 17, 0),
        status=BookingStatus.CONFIRMED
    )

    test_session.add_all([b1, b2, b3])
    test_session.commit()
    return [b1, b2, b3]
