import os
import pytest
from eduroomapp.admin import UserView

@pytest.fixture
def data_dir():
    return os.path.join(os.path.dirname(__file__), 'data')


def test_all_valid(data_dir):
    users = UserView.get_user_from_csv(os.path.join(data_dir, 'valid_user.csv'))

    assert len(users) == 10
    for u in users:
        assert isinstance(u, dict)
        assert 'fullname' in u and u['fullname']
        assert 'username' in u and u['username']
        assert 'email' in u and u['email']
        assert 'password' in u and u['password']
        assert 'user_role' in u and u['user_role']
    assert users[0]['username'] == '2351010229' and users[0]['fullname'] == 'Nguyen Van Tuan'
    assert users[-1]['username'] == '2351010666' and users[-1]['fullname'] == 'Tran Gia Huy'


def test_empty_user(data_dir):
    with pytest.raises(ValueError):
        UserView.get_user_from_csv(os.path.join(data_dir, "empty_user.csv"))


def test_missing_colnum_user(data_dir):
    with pytest.raises(ValueError):
        UserView.get_user_from_csv(os.path.join(data_dir, "missing_colnum_user.csv"))


def test_null_data_user(data_dir):
    with pytest.raises(ValueError):
        UserView.get_user_from_csv(os.path.join(data_dir, "null_data_user.csv"))


def test_invalid_role_user(data_dir):
    with pytest.raises(ValueError):
        UserView.get_user_from_csv(os.path.join(data_dir, "invalid_role_user.csv"))

