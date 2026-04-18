import hashlib
import random
import re
import secrets
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from sqlalchemy.sql.functions import func

from eduroomapp import db, app
from eduroomapp.models import User, UserRole, Room, RoomStatus, Booking, BookingStatus


def get_user_role():
    return [role for role in UserRole if role.value != 1]


def get_user_by_id(id):
    return User.query.get(id)


def get_user_by_email(email):
    return db.session.query(User).filter(User.email == email).first()


def get_user_by_username(username):
    return db.session.query(User).filter(User.username == username).first()


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()


def add_user(fullname, username, password, user_role, email):
    if User.query.filter(User.username == username).first():
        raise ValueError("Username đã tồn tại")

    if User.query.filter(User.email == email).first():
        raise ValueError("Địa chỉ Email này đã được đăng ký!")

    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(fullname=fullname.strip(),
             username=username.strip(),
             password=password,
             user_role=user_role,
             email=email.strip())
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Username đã tồn tại!')


def create_user_from_google(google_email, google_name):
    base_username = google_email.split('@')[0]
    username = base_username

    count = 1
    while db.session.query(User).filter(User.username == username).first():
        username = f"{base_username}{count}"
        count += 1

    random_password = secrets.token_hex(8)
    hashed_password = str(hashlib.md5(random_password.encode('utf-8')).hexdigest())

    user = User(
        fullname=google_name,
        username=username,
        email=google_email,
        password=hashed_password,
        user_role=UserRole.STUDENT
    )

    db.session.add(user)
    try:
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise Exception("Lỗi Database khi lưu tài khoản Google!")


def create_user_from_facebook(fb_id, fb_name, fb_email):
    if fb_email:
        base_username = fb_email.split('@')[0]
    else:
        base_username = f"fb_{fb_id}"

    username = base_username
    count = 1
    while db.session.query(User).filter(User.username == username).first():
        username = f"{base_username}{count}"
        count += 1

    random_password = secrets.token_hex(8)
    hashed_password = str(hashlib.md5(random_password.encode('utf-8')).hexdigest())

    user = User(
        fullname=fb_name,
        username=username,
        email=fb_email,
        password=hashed_password,
        user_role=UserRole.STUDENT
    )

    db.session.add(user)
    try:
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise Exception("Lỗi Database khi lưu tài khoản Facebook!")


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


def get_bookings_user(user_id):
    bookings = (db.session.query(Booking)
                .filter(Booking.user_id == user_id)
                .order_by(Booking.created_at.desc())
                .all())
    return bookings


def get_booking_count_today(user_id, today_date):
    count = db.session.query(Booking).filter(
        Booking.user_id == user_id,
        func.date(Booking.start_time) == today_date,
        Booking.status == BookingStatus.CONFIRMED
    ).count()
    return count


def get_booking_count_week(user_id, start_week, end_week):
    count = db.session.query(Booking).filter(
        Booking.user_id == user_id,
        func.date(Booking.start_time) >= start_week,
        func.date(Booking.start_time) <= end_week,
        Booking.status == BookingStatus.CONFIRMED
    ).count()
    return count


def get_cancel_count_week(user_id, start_week, end_week):
    count = db.session.query(Booking).filter(
        Booking.user_id == user_id,
        func.date(Booking.start_time) >= start_week,
        func.date(Booking.start_time) <= end_week,
        Booking.status == BookingStatus.CANCELED
    ).count()
    return count


def cancel_booking_logic(booking_id, user_id):
    booking = db.session.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user_id
    ).first()

    if not booking:
        raise Exception("Không tìm thấy lịch đặt!")

    now = datetime.now()
    time_diff = booking.start_time - now
    if time_diff < timedelta(minutes=30):
        raise Exception("Không thể hủy vì chỉ còn chưa đầy 30 phút là đến giờ sử dụng!")

    booking.status = BookingStatus.CANCELED

    start_week = now.date() - timedelta(days=now.date().weekday())
    end_week = start_week + timedelta(days=6)
    cancel_count = get_cancel_count_week(user_id, start_week, end_week)

    if cancel_count >= 5:
        user = db.session.query(User).get(user_id)
        user.locked_until = now + timedelta(hours=24)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Lỗi hệ thống: {e}")
