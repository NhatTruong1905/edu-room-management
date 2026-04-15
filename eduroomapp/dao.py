import hashlib
import random
import re
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from eduroomapp import db, app
from eduroomapp.models import User, UserRole, Room, RoomStatus, Booking, BookingStatus


def get_user_role():
    return [role for role in UserRole if role.value != 1]


def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()


def add_user(fullname, username, password, user_role):
    if User.query.filter(User.username == username).first():
        raise ValueError("Username đã tồn tại")

    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(fullname=fullname.strip(), username=username.strip(), password=password, user_role=user_role)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Username đã tồn tại!')


def get_rooms():
    return Room.query.all()


def get_rooms_by_date_and_time(start_time, end_time, capacity=None, page=1):
    booked_subquery = db.session.query(Booking.room_id).filter(
        Booking.start_time < end_time,
        Booking.end_time > start_time,
        Booking.status == BookingStatus.CONFIRMED
    ).subquery()

    query = db.session.query(
        Room,
        booked_subquery.c.room_id.isnot(None).label('is_booked')
    ).outerjoin(
        booked_subquery, Room.id == booked_subquery.c.room_id
    )

    if capacity:
        try:
            query = query.filter(Room.capacity >= int(capacity))
        except ValueError:
            pass

    total_count = query.count()
    offset = (page - 1) * app.config["PAGE_SIZE"]
    rooms = query.offset(offset).limit(app.config["PAGE_SIZE"]).all()
    return rooms, total_count


def add_booking(user_id, room_id, start_time, end_time):
    booking = Booking(
        user_id=user_id,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED
    )
    db.session.add(booking)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Lỗi lưu đặt phòng: {e}")
