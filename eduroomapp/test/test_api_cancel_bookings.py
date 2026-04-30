from eduroomapp.test.test_base import auth_client, test_client, test_app, test_session
import pytest


def test_api_cancel_booking_success(auth_client, mocker):
    test_client, fake_user = auth_client

    mock_cancel = mocker.patch('eduroomapp.dao.cancel_booking')
    res = test_client.post('/api/bookings/10')
    assert res.status_code == 200

    data = res.get_json()
    assert data['success'] is True
    assert data['message'] == "Hủy phòng thành công!"

    mock_cancel.assert_called_once_with(booking_id=10, user_id=fake_user.id)


@pytest.mark.parametrize("error_msg", [
    "Không tìm thấy lịch đặt!",
    "Không được phép hủy thêm! Tài khoản của bạn bị khóa 24h vì vượt quá giới hạn hủy tuần này!",
    "Không thể hủy vì chỉ còn chưa đầy 30 phút là đến giờ sử dụng!"
])
def test_api_cancel_booking_exception(auth_client, error_msg, mocker):
    test_client, fake_user = auth_client

    mock_cancel = mocker.patch('eduroomapp.dao.cancel_booking', side_effect=Exception(error_msg))

    res = test_client.post('/api/bookings/10')
    assert res.status_code == 400

    data = res.get_json()
    assert data['success'] is False
    assert data['message'] == error_msg

    mock_cancel.assert_called_once_with(booking_id=10, user_id=fake_user.id)
