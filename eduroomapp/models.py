import enum
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql.functions import func
from flask_login import UserMixin

from eduroomapp import db, app
from sqlalchemy import Column, String, Integer, Boolean, Enum, DateTime, ForeignKey, CheckConstraint


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)


class RoomStatus(enum.Enum):
    AVAILABLE = 1
    MAINTENANCE = 2


class Room(BaseModel):
    __tablename__ = 'room'
    __table_args__ = (
        CheckConstraint('capacity >= 5 AND capacity <= 200', name='check_room_capacity'),
        {'extend_existing': True}
    )
    name = Column(String(50), nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE, nullable=False)

    bookings = relationship('Booking', back_populates='room')

    @validates('capacity')
    def validate_capacity(self, key, capacity):
        if capacity < 5 or capacity > 200:
            raise ValueError('Sức chứa phải từ 5 đến 200.')
        return capacity


class UserRole(enum.Enum):
    ADMIN = 1
    TEACHER = 2
    STUDENT = 3


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
    locked_until = Column(DateTime, nullable=True)

    bookings = relationship('Booking', back_populates='user')


class BookingStatus(enum.Enum):
    CONFIRMED = 1
    CANCELED = 2


class Booking(BaseModel):
    __tablename__ = 'booking'
    __table_args__ = {'extend_existing': True}
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id', ondelete='SET NULL'), nullable=True)

    user = relationship('User', back_populates='bookings')
    room = relationship('Room', back_populates='bookings')


def add_data():
    admin = User(fullname="Nguyễn Quản Trị", username="admin1",
                 password="$2a$12$wV/sS6FXhLkHizb9eE53XOd78yFywL8hwO.LhuMPylOFn69RZ/NdK",
                 user_role=UserRole.ADMIN)
    gv1 = User(fullname="Trần Tiến Sĩ", username="gv01",
               password="$2a$12$9pRZbqk9J5Yz80zNRHEP6eYumL4CiKvdnFEhXCreZG0JrbYSvSF4K",
               user_role=UserRole.TEACHER, email="t1@gmail.com")
    gv2 = User(fullname="Lê Thạc Sĩ", username="gv02",
               password="$2a$12$Fvc8rkfUYlvHnZ99fN9yLeopgH9csqbLAsU3G6U5u0Ro3V0In53tO",
               user_role=UserRole.TEACHER, email="t2@gmail.com")
    sv1 = User(fullname="Phạm Học Bá", username="sv01",
               password="$2a$12$ZszMfBOtxilJqluWAz776eCKWCtUc6ww5P2hhq6ZhTSwANSUwIaUy",
               user_role=UserRole.STUDENT, email="t3@gmail.com")
    sv2 = User(fullname="Hoàng Chăm Chỉ", username="sv02",
               password="$2a$12$ivVCJGUaa/2w2hPUh3loeejQ0KapOS7LQaDSOhDslylN1N8UjkFFm",
               user_role=UserRole.STUDENT, email="t4@gmail.com")
    s3 = User(fullname="Phùng Thanhh Độ", username="sv03",
              password="$2a$12$hwYcOJp4YeJP7ffRmOvjVux5mk6ZegrijGcun1HBEWJnC5dwgixEm",
              user_role=UserRole.TEACHER, email="t5@gmail.com")
    s4 = User(fullname="Phạm Văn Tày", username="sv04",
              password="$2a$12$Z6vEZCIMsZyQRlnznVNqhOE6cKGoC.mxk8d4l/xTB7aJH2UL4/q1i",
              user_role=UserRole.STUDENT, email="t6@gmail.com")
    db.session.add_all([admin, gv1, gv2, sv1, sv2, s3, s4])
    db.session.commit()

    r1 = Room(name="A101", capacity=50, status=RoomStatus.AVAILABLE)
    r2 = Room(name="A102", capacity=30, status=RoomStatus.AVAILABLE)
    r3 = Room(name="B201", capacity=100, status=RoomStatus.AVAILABLE)
    r4 = Room(name="C305", capacity=200, status=RoomStatus.AVAILABLE)
    r5 = Room(name="D404", capacity=40, status=RoomStatus.MAINTENANCE)
    r6 = Room(name="E501", capacity=45, status=RoomStatus.AVAILABLE)
    r7 = Room(name="Lap 01", capacity=30, status=RoomStatus.AVAILABLE)
    r8 = Room(name="Lap 02", capacity=30, status=RoomStatus.MAINTENANCE)
    r9 = Room(name="Hall A", capacity=50, status=RoomStatus.AVAILABLE)
    r10 = Room(name="Meeting Room 1", capacity=10, status=RoomStatus.AVAILABLE)
    r11 = Room(name="Library Quiet Room", capacity=15, status=RoomStatus.AVAILABLE)
    r12 = Room(name="Workshop B", capacity=60, status=RoomStatus.AVAILABLE)
    r13 = Room(name="E502", capacity=45, status=RoomStatus.AVAILABLE)
    r14 = Room(name="Studio 1", capacity=20, status=RoomStatus.AVAILABLE)
    r15 = Room(name="A202", capacity=40, status=RoomStatus.AVAILABLE)

    db.session.add_all([r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15])
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
