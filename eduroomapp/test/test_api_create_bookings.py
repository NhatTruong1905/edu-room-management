from datetime import timedelta, datetime
from eduroomapp.test.test_base import test_session, test_client, test_app, auth_client


def test_api_create_booking_missing_info(auth_client):
    test_client, _ = auth_client
    form_data = {
        'room_id': '1',
        'booking_date': '2026-04-30',
        'booking_start_time': '09:00'
    }
    res = test_client.post('/api/bookings', data=form_data)
    assert res.status_code == 302
    assert res.headers['Location'] == '/booking'

    with test_client.session_transaction() as session:
        flashes = session.get('_flashes', [])
        assert ('danger', 'Lỗi: Thiếu thông tin đặt phòng!') in flashes


def test_api_create_booking_locked_user(auth_client):
    test_client, fake_user = auth_client

    fake_user.locked_until = datetime.now() + timedelta(days=1)
    form_data = {
        'room_id': '1',
        'booking_date': '2026-04-30',
        'booking_start_time': '09:00',
        'booking_end_time': '11:00'
    }
    res = test_client.post('/api/bookings', data=form_data)
    assert res.status_code == 302
    assert res.headers['Location'] == '/booking'

    with test_client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
        assert ('danger', 'Tài khoản của bạn đang bị khóa quyền đặt phòng do hủy quá nhiều lần!') in flashes


def test_api_create_booking_limit_daily(auth_client, mocker):
    test_client, fake_user = auth_client

    mocker.patch('eduroomapp.dao.get_booking_count_today', return_value=3)
    form_data = {
        'room_id': '1',
        'booking_date': '2026-04-30',
        'booking_start_time': '09:00',
        'booking_end_time': '11:00'
    }
    res = test_client.post('/api/bookings', data=form_data)
    assert res.status_code == 302
    assert res.headers['Location'] == '/booking'

    with test_client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
        assert ('warning', 'Đã giới hạn đặt quá 3 phòng / ngày!') in flashes


def test_api_create_booking_limit_weekly(auth_client, mocker):
    test_client, fake_user = auth_client

    mocker.patch('eduroomapp.dao.get_booking_count_today', return_value=1)
    mocker.patch('eduroomapp.dao.get_booking_count_week', return_value=10)
    form_data = {
        'room_id': '1',
        'booking_date': '2026-04-30',
        'booking_start_time': '09:00',
        'booking_end_time': '11:00'
    }
    res = test_client.post('/api/bookings', data=form_data)
    assert res.status_code == 302
    assert res.headers['Location'] == '/booking'

    with test_client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
        assert ('warning', 'Đã giới hạn quá 10 phòng / tuần!') in flashes


def test_api_create_booking_success(auth_client, mocker):
    test_client, fake_user = auth_client

    mocker.patch('eduroomapp.dao.get_booking_count_today', return_value=1)
    mocker.patch('eduroomapp.dao.get_booking_count_week', return_value=2)
    mock_add = mocker.patch('eduroomapp.dao.add_booking')
    form_data = {
        'room_id': '1',
        'booking_date': '2026-04-30',
        'booking_start_time': '09:00',
        'booking_end_time': '11:00'
    }
    res = test_client.post('/api/bookings', data=form_data)
    assert res.status_code == 302
    mock_add.assert_called_once()

    start_time = datetime.strptime("2026-04-30 09:00", "%Y-%m-%d %H:%M")
    end_time = datetime.strptime("2026-04-30 11:00", "%Y-%m-%d %H:%M")
    mock_add.assert_called_with(
        user_id=fake_user.id,
        room_id='1',
        start_time=start_time,
        end_time=end_time
    )

    with test_client.session_transaction() as session:
        flashes = session.get('_flashes', [])
        assert ('success', 'Đặt phòng thành công!') in flashes


def test_api_create_booking_system_error(auth_client, mocker):
    test_client, fake_user = auth_client

    mocker.patch('eduroomapp.index.dao.get_booking_count_today', return_value=1)
    mocker.patch('eduroomapp.index.dao.get_booking_count_week', return_value=2)
    mocker.patch('eduroomapp.index.dao.add_booking', side_effect=Exception("Database Exception"))

    form_data = {
        'room_id': '1',
        'booking_date': '2026-04-30',
        'booking_start_time': '09:00',
        'booking_end_time': '11:00'
    }
    res = test_client.post('/api/bookings', data=form_data)
    assert res.status_code == 302

    with test_client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
        assert ('danger', 'Đặt phòng thất bại. Vui lòng thử lại! \n Lỗi: Database Exception') in flashes


def test_api_create_booking_invalid_time(auth_client):
    test_client, fake_user = auth_client

    form_data = {
        'room_id': '1',
        'booking_date': '2026-04-30',
        'booking_start_time': '11:00',
        'booking_end_time': '09:00'
    }
    res = test_client.post('/api/bookings', data=form_data)
    assert res.status_code == 302

    with test_client.session_transaction() as session:
        flashes = session.get('_flashes', [])
        assert ('danger', 'Lỗi: Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc!') in flashes


def test_api_create_booking_outside_business_hours(auth_client):
    test_client, fake_user = auth_client

    form_data = {
        'room_id': '1',
        'booking_date': '2026-04-30',
        'booking_start_time': '22:00',
        'booking_end_time': '23:00'
    }

    res = test_client.post('/api/bookings', data=form_data)
    assert res.status_code == 302

    with test_client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
        assert ('danger', 'Lỗi: Chỉ được phép đặt phòng trong khung giờ từ 07:00 đến 21:00!') in flashes
