import hashlib
import re
import secrets
from datetime import datetime, timedelta

import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from sqlalchemy.sql.functions import func
import pandas as pd

from eduroomapp import db, app
from eduroomapp.models import User, UserRole, Room, RoomStatus, Booking, BookingStatus, add_data
from eduroomapp.exceptions import DeleteRoomException, EmptyRoomException


def get_user_role():
    return [role for role in UserRole if role.value != 1]


def get_user_by_id(id):
    return User.query.get(id)


def get_user_by_email(email):
    return db.session.query(User).filter(User.email == email).first()


def get_user_by_username(username):
    return db.session.query(User).filter(User.username == username).first()


def auth_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        input_password_bytes = password.strip().encode('utf-8')
        stored_password_bytes = user.password.encode('utf-8')
        if bcrypt.checkpw(input_password_bytes, stored_password_bytes):
            return user
    return None


def add_user(fullname, username, password, user_role, email):
    fullname = fullname.strip()
    username = username.strip()
    password = password.strip()
    email = email.strip()

    if len(username) < 4:
        raise ValueError("Username tối thiểu 4 ký tự")

    if len(password) < 3:
        raise ValueError("Password tối thiểu 3 ký tự")

    if not re.search(r'(@gmail\.com|@.*\.edu\.vn)$', email):
        raise ValueError("Email phải có đuôi @gmail.com hoặc định dạng @tên_trường.edu.vn")

    if User.query.filter(User.username == username).first():
        raise ValueError("Username đã tồn tại")

    if User.query.filter(User.email == email).first():
        raise ValueError("Địa chỉ Email này đã được đăng ký!")

    raw_password = password.encode('utf-8')
    hashed_bytes = bcrypt.hashpw(raw_password, bcrypt.gensalt(12))
    password = hashed_bytes.decode('utf-8')
    u = User(fullname=fullname,
             username=username,
             password=password,
             user_role=user_role,
             email=email)
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
    byte_password = random_password.strip().encode('utf-8')
    hashed_bytes = bcrypt.hashpw(byte_password, bcrypt.gensalt(12))
    hashed_password = hashed_bytes.decode('utf-8')

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
    byte_password = random_password.strip().encode('utf-8')
    hashed_bytes = bcrypt.hashpw(byte_password, bcrypt.gensalt(12))
    hashed_password = hashed_bytes.decode('utf-8')

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
    if start_time >= end_time:
        raise ValueError("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc!")

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


def cancel_booking(booking_id, user_id):
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

    if cancel_count > 5:
        user = db.session.query(User).get(user_id)
        user.locked_until = now + timedelta(hours=24)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Lỗi hệ thống: {e}")

    if cancel_count > 5:
        raise Exception("Không được phép hủy thêm! Tài khoản của bạn bị khóa 24h vì vượt quá giới hạn hủy tuần này!")


def get_booking_of_user(user_id, room_id):
    return db.session.query(Booking).filter(Booking.room_id == room_id, Booking.user_id == user_id).first()


def delete_room(room_id, current_user):
    if not current_user or current_user.user_role != UserRole.ADMIN:
        raise PermissionError("Bạn không có quyền thực hiện thao tác này!")

    room = Room.query.get(room_id)
    if not room:
        raise EmptyRoomException("Phòng không tồn tại!")

    future_booking = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.start_time > datetime.now(),
        Booking.status == BookingStatus.CONFIRMED
    ).first()

    if future_booking:
        raise DeleteRoomException(f"Phòng đang có lịch đặt trong tương lai, không thể xoá!")

    try:
        db.session.delete(room)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e