import enum
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from flask_login import UserMixin
from eduroomapp import db, app
from sqlalchemy import Column, String, Integer, Boolean, Enum, DateTime, ForeignKey


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)


class RoomStatus(enum.Enum):
    AVAILABLE = 1
    MAINTENANCE = 2


class Room(BaseModel):
    __tablename__ = 'room'
    name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE, nullable=False)

    bookings = relationship('Booking', back_populates='room')


class UserRole(enum.Enum):
    ADMIN = 1
    TEACHER = 2
    STUDENT = 3


class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    fullname = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
    locked_until = Column(DateTime, nullable=True)

    bookings = relationship('Booking', back_populates='user')


class BookingStatus(enum.Enum):
    CONFIRMED = 1
    CANCELED = 2


class Booking(BaseModel):
    __tablename__ = 'booking'

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id', ondelete='RESTRICT'), nullable=False)

    user = relationship('User', back_populates='bookings')
    room = relationship('Room', back_populates='bookings')


def add_data():
    admin = User(fullname="Nguyễn Quản Trị", username="admin", password="202cb962ac59075b964b07152d234b70",
                 user_role=UserRole.ADMIN)

    gv1 = User(fullname="Trần Tiến Sĩ", username="gv01", password="202cb962ac59075b964b07152d234b70",
               user_role=UserRole.TEACHER)
    gv2 = User(fullname="Lê Thạc Sĩ", username="gv02", password="202cb962ac59075b964b07152d234b70",
               user_role=UserRole.TEACHER)

    sv1 = User(fullname="Phạm Học Bá", username="sv01", password="202cb962ac59075b964b07152d234b70",
               user_role=UserRole.STUDENT)
    sv2 = User(fullname="Hoàng Chăm Chỉ", username="sv02", password="202cb962ac59075b964b07152d234b70",
               user_role=UserRole.STUDENT)
    sv3_locked = User(fullname="Spam Hủy", username="sv03", password="202cb962ac59075b964b07152d234b70",
                      user_role=UserRole.STUDENT,
                      locked_until=datetime.now() + timedelta(hours=20))

    db.session.add_all([admin, gv1, gv2, sv1, sv2, sv3_locked])
    db.session.commit()

    r1 = Room(name="A101", capacity=50, status=RoomStatus.AVAILABLE)
    r2 = Room(name="A102", capacity=30, status=RoomStatus.AVAILABLE)
    r3 = Room(name="B201", capacity=100, status=RoomStatus.AVAILABLE)
    r4 = Room(name="C305", capacity=200, status=RoomStatus.AVAILABLE)
    r5_maintenance = Room(name="D404", capacity=40, status=RoomStatus.MAINTENANCE)

    db.session.add_all([r1, r2, r3, r4, r5_maintenance])
    db.session.commit()

    now = datetime.now()
    b1 = Booking(
        start_time=now.replace(hour=8, minute=0, second=0) + timedelta(days=1),
        end_time=now.replace(hour=10, minute=0, second=0) + timedelta(days=1),
        status=BookingStatus.CONFIRMED,
        user_id=sv1.id,
        room_id=r1.id
    )

    b2 = Booking(
        start_time=now.replace(hour=13, minute=0, second=0) + timedelta(days=2),
        end_time=now.replace(hour=16, minute=0, second=0) + timedelta(days=2),
        status=BookingStatus.CONFIRMED,
        user_id=gv1.id,
        room_id=r4.id
    )

    b3 = Booking(
        start_time=now.replace(hour=9, minute=0, second=0) + timedelta(days=3),
        end_time=now.replace(hour=11, minute=0, second=0) + timedelta(days=3),
        status=BookingStatus.CANCELED,
        user_id=sv2.id,
        room_id=r2.id
    )

    b4 = Booking(
        start_time=now.replace(hour=14, minute=0, second=0) + timedelta(days=1),
        end_time=now.replace(hour=16, minute=0, second=0) + timedelta(days=1),
        status=BookingStatus.CONFIRMED,
        user_id=sv1.id,
        room_id=r3.id
    )

    db.session.add_all([b1, b2, b3, b4])
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        add_data()
