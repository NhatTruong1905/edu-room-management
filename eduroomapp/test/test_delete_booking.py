import pytest

from eduroomapp.dao import delete_room
from eduroomapp.exceptions import DeleteRoomException, EmptyRoomException
from eduroomapp.models import Room
from eduroomapp.test.test_base import test_app, test_session, sample_bookings, sample_users, sample_rooms, sample_admin


def test_delete_room_as_admin_success(test_app, test_session, sample_admin, sample_rooms):
    room_id = sample_rooms[1].id

    result = delete_room(room_id, sample_admin)

    assert result is True
    assert Room.query.get(room_id) is None


def test_delete_room_as_student_fail(test_app, test_session, sample_users, sample_rooms):
    student = sample_users[1]
    room_id = sample_rooms[0].id

    with pytest.raises(PermissionError):
        delete_room(room_id, student)

    assert Room.query.get(room_id) is not None


def test_delete_room_has_future_booking_fail(test_app, test_session, sample_admin, sample_bookings):
    future_booking = sample_bookings[3]
    room_id = future_booking.room_id

    with pytest.raises(DeleteRoomException) as e:
        delete_room(room_id, sample_admin)

    assert "Phòng đang có lịch đặt trong tương lai" in str(e.value)
    assert Room.query.get(room_id) is not None


def test_delete_room_not_found(test_app, test_session, sample_admin):
    invalid_id = 9999

    with pytest.raises(EmptyRoomException) as e:
        delete_room(invalid_id, sample_admin)

    assert "Phòng không tồn tại!" in str(e.value)
