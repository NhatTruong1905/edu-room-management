from datetime import datetime, timedelta
import pytest
from eduroomapp.models import BookingStatus, Booking
from eduroomapp.test.test_base import sample_rooms, test_app, test_session, sample_bookings, sample_users
from eduroomapp import dao
from sqlalchemy.exc import IntegrityError


def test_cancel_bookings_success(test_session, sample_rooms, sample_users, mocker):
    u1, u2 = sample_users
    r1, r2, r3, r4 = sample_rooms

    now = datetime.now()
    start_time = now + timedelta(hours=24)
    end_time = start_time + timedelta(hours=24)
    b = Booking(
        room_id=r1.id,
        user_id=u1.id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED
    )
    test_session.add(b)
    test_session.commit()

    mock_get = mocker.patch('eduroomapp.dao.get_cancel_count_week', return_value=1)
    dao.cancel_booking(b.id, u1.id)

    assert b.status == BookingStatus.CANCELED
    assert u1.locked_until is None

    mock_get.assert_called_once()


def test_cancel_not_bookings(test_session, sample_rooms, sample_users):
    u1, u2 = sample_users
    r1, r2, r3, r4 = sample_rooms

    now = datetime.now()
    start_time = now + timedelta(hours=24)
    end_time = start_time + timedelta(hours=24)
    b = Booking(
        room_id=r1.id,
        user_id=u1.id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED
    )
    test_session.add(b)
    test_session.commit()

    with pytest.raises(Exception, match='Không tìm thấy lịch đặt!'):
        dao.cancel_booking(b.id, u2.id)


def test_cancel_bookings_under_30_minutes(test_session, sample_rooms, sample_users):
    u1, u2 = sample_users
    r1, r2, r3, r4 = sample_rooms

    now = datetime.now()
    start_time = now + timedelta(minutes=15)
    end_time = start_time + timedelta(hours=2)
    b = Booking(
        room_id=r1.id,
        user_id=u1.id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED
    )
    test_session.add(b)
    test_session.commit()

    with pytest.raises(Exception, match='Không thể hủy vì chỉ còn chưa đầy 30 phút là đến giờ sử dụng!'):
        dao.cancel_booking(b.id, u1.id)


def test_cancel_bookings_lock_account(test_session, sample_rooms, sample_users, mocker):
    u1, u2 = sample_users
    r1, r2, r3, r4 = sample_rooms

    now = datetime.now()
    start_time = now + timedelta(hours=24)
    end_time = start_time + timedelta(hours=24)
    b = Booking(
        room_id=r1.id,
        user_id=u1.id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED
    )
    test_session.add(b)
    test_session.commit()

    mock_get = mocker.patch('eduroomapp.dao.get_cancel_count_week', return_value=6)
    with pytest.raises(Exception,
                       match='Không được phép hủy thêm! Tài khoản của bạn bị khóa 24h vì vượt quá giới hạn hủy tuần này!'):
        dao.cancel_booking(b.id, u1.id)

    assert b.status == BookingStatus.CANCELED
    assert u1.locked_until is not None
    assert u1.locked_until > now
    mock_get.assert_called_once()


def test_cancel_bookings_failure(test_session, sample_rooms, sample_users, mocker):
    u1, u2 = sample_users
    r1, r2, r3, r4 = sample_rooms

    now = datetime.now()
    start_time = now + timedelta(hours=24)
    end_time = start_time + timedelta(hours=24)
    b = Booking(
        room_id=r1.id,
        user_id=u1.id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED
    )
    test_session.add(b)
    test_session.commit()

    mocker.patch('eduroomapp.dao.get_cancel_count_week', return_value=0)
    mock_commit = mocker.patch('eduroomapp.db.session.commit', side_effect=IntegrityError(None, None, None))
    mock_rollback = mocker.patch('eduroomapp.db.session.rollback')

    with pytest.raises(Exception, match="Lỗi hệ thống:"):
        dao.cancel_booking(b.id, u1.id)

    mock_commit.assert_called_once()
    mock_rollback.assert_called_once()
