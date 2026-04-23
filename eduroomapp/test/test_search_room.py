from datetime import datetime
from eduroomapp import dao
from eduroomapp.test.test_base import sample_rooms, test_app, test_session, sample_bookings
from eduroomapp.dao import get_rooms


def test_all(sample_rooms):
    actual_rooms = get_rooms()

    assert len(actual_rooms) == len(sample_rooms)


def test_get_rooms_booked_overlap(test_app, test_session, sample_rooms, sample_bookings):
    start = datetime(2026, 4, 20, 10, 0)
    end = datetime(2026, 4, 20, 10, 30)

    rooms, count = dao.get_rooms_by_date_and_time(start, end)

    for r, is_booked in rooms:
        if r.name == "A101":
            assert is_booked is True
        elif r.name == "A102":
            assert is_booked is False
        elif r.name == "A103":
            assert is_booked is False
