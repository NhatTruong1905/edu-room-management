from datetime import datetime, timedelta

import pytest

from eduroomapp.test.test_base import test_session, sample_users, sample_rooms, sample_bookings, test_app
from eduroomapp import dao


def test_add_bookings_success(test_session, sample_rooms, sample_users):
    u1, u2 = sample_users
    r1, r2, r3, r4 = sample_rooms

    start_time = datetime.now()
    end_time = start_time + timedelta(hours=24)
    dao.add_booking(u1.id, r4.id, start_time, end_time)

    booking = dao.get_booking_of_user(u1.id, r4.id)

    assert booking is not None
    assert booking.user_id == u1.id
    assert booking.room_id == r4.id


def test_add_bookings_failure(test_session, sample_rooms, sample_users, mocker):
    u1, u2 = sample_users
    r1, r2, r3, r4 = sample_rooms

    start_time = datetime.now()
    end_time = start_time + timedelta(hours=24)
    dao.add_booking(u1.id, r4.id, start_time, end_time)

    mock_commit = mocker.patch('eduroomapp.db.session.commit', side_effect=Exception)

    with pytest.raises(Exception, match='Lỗi lưu đặt phòng:'):
        dao.add_booking(u1.id, r4.id, start_time, end_time)

    mock_commit.assert_called_once()
