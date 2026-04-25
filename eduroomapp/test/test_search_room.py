from datetime import datetime
from eduroomapp import dao
from eduroomapp.test.test_base import sample_rooms, test_app, test_session, sample_bookings, sample_users
from eduroomapp.dao import get_rooms


def test_all(sample_rooms):
    actual_rooms = get_rooms()

    assert len(actual_rooms) == len(sample_rooms)


def test_get_rooms_capacity(test_app, test_session, sample_rooms):
    start = datetime(2026, 4, 20, 14, 0)
    end = datetime(2026, 4, 20, 15, 0)

    rooms, count = dao.get_rooms_by_date_and_time(start, end, capacity=55)

    assert count == 2
    room_names = [r.name for r, is_booked in rooms]
    assert "A102" in room_names
    assert "A103" in room_names
    assert "A101" not in room_names


def test_get_rooms_pagination(test_app, test_session, sample_rooms, sample_bookings, sample_users):
    start = datetime(2026, 4, 20, 9, 0)
    end = datetime(2026, 4, 20, 17, 0)

    rooms_page1, count = dao.get_rooms_by_date_and_time(start, end, page=1)
    assert len(rooms_page1) == 2
    assert count == 4

    rooms_page2, _ = dao.get_rooms_by_date_and_time(start, end, page=2)
    assert len(rooms_page2) == 2

    names_p1 = [r.name for r, _ in rooms_page1]
    names_p2 = [r.name for r, _ in rooms_page2]
    for name in names_p1:
        assert name not in names_p2


def test_get_rooms_capacity_pagination(test_app, test_session, sample_rooms, sample_bookings, sample_users):
    start = datetime(2026, 4, 20, 9, 0)
    end = datetime(2026, 4, 20, 17, 0)

    rooms_page1, count = dao.get_rooms_by_date_and_time(start, end, capacity=100, page=1)
    assert len(rooms_page1) == 1
    assert count == 1

    rooms_page2, count2 = dao.get_rooms_by_date_and_time(start, end, capacity=100, page=2)
    assert len(rooms_page2) == 0
    assert count2 == 0



def test_get_rooms_is_booked_status(test_app, test_session, sample_rooms, sample_bookings):
    start_search = datetime(2026, 4, 20, 10, 0)
    end_search = datetime(2026, 4, 20, 12, 0)

    rooms, _ = dao.get_rooms_by_date_and_time(start_search, end_search)

    for r, is_booked in rooms:
        if r.name == "A101":
            assert is_booked is True
        else:
            assert is_booked is False


def test_get_rooms_boundary_time(test_app, test_session, sample_rooms, sample_bookings):
    start_search = datetime(2026, 4, 20, 11, 0)
    end_search = datetime(2026, 4, 20, 13, 0)

    rooms, _ = dao.get_rooms_by_date_and_time(start_search, end_search)
    is_booked_a101 = [is_booked for r, is_booked in rooms if r.name == "A101"][0]
    assert is_booked_a101 is False
