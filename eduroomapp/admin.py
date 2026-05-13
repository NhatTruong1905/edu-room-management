from datetime import datetime

import pandas as pd
import hashlib
import bcrypt
from flask import request, redirect, url_for, flash
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms.validators import DataRequired, NumberRange

from eduroomapp.models import UserRole, Room, User, Booking, BookingStatus
from eduroomapp import admin, db, dao
from eduroomapp.dao import add_user
from eduroomapp.exceptions import DeleteRoomException, EmptyRoomException


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class BaseModelAdminView(ModelView):
    column_display_pk = True
    edit_modal = True
    page_size = 10


class RoomView(AuthenticatedAdmin, BaseModelAdminView):
    column_filters = ['id', 'name', 'capacity']
    column_searchable_list = ['name']

    form_excluded_columns = ['bookings']

    column_labels = {
        'id': 'Mã phòng',
        'name': 'Tên phòng',
        'capacity': 'Sức chứa'
    }

    form_args = {
        'capacity': {'validators': [DataRequired(), NumberRange(min=5, max=200, message='Sức chứa phải từ 5 đến 200.')]
        }
    }

    def delete_model(self, model):
        try:
            dao.delete_room(model.id, current_user)
            flash(f'Đã xoá phòng {model.name} thành công.', 'success')
            return True
        except PermissionError as pe:
            flash(str(pe), 'error')
            return False
        except EmptyRoomException as e:
            flash(str(e), 'error')
            return False
        except DeleteRoomException as e:
            flash(str(e), 'error')
            return False


class UserView(AuthenticatedAdmin, BaseModelAdminView):
    list_template = 'admin/user_menu_bar.html'
    column_list = ['id', 'fullname', 'username', 'email', 'user_role', 'locked_until']
    column_filters = ['user_role', 'locked_until']
    column_searchable_list = ['username', 'email', 'fullname']

    column_labels = {
        'id': 'ID',
        'fullname': 'Họ tên',
        'username': 'Tên đăng nhập',
        'email': 'Email',
        'user_role': 'Vai trò',
        'locked_until': 'Khóa đến'
    }

    form_excluded_columns = ['bookings']

    def on_model_change(self, form, model, is_created):
        if model.password:
            byte_password = model.password.encode('utf-8')
            hash_password = bcrypt.hashpw(byte_password, bcrypt.gensalt(12))
            model.password = hash_password.decode('utf-8')

    @expose('/import-csv', methods=['POST'])
    def import_csv(self):
        file = request.files.get('file')
        user_role = {'STUDENT', 'TEACHER'}

        try:
            users = UserView.get_user_from_csv(file, user_role)
            for u in users:
                add_user(**u)
            flash(f'Thêm thành công tài khoản')
        except Exception as e:
            flash(str(e))

        return redirect(url_for('.index_view'))

    @expose('/import-csv', methods=['GET'])
    def import_csv_view(self):
        return self.render('admin/import_csv_view.html')

    @staticmethod
    def get_user_from_csv(file, user_role={'STUDENT', 'TEACHER'}):
        try:
            df = pd.read_csv(file)
        except Exception as e:
            raise ValueError(f'Cannot read csv file: {e}')
        if df.empty:
            raise ValueError('CSV file is empty')

        df.columns = df.columns.str.strip()

        missing_columns = {'fullname', 'username', 'email', 'cccd', 'user_role'} - set(df.columns)
        if missing_columns:
            raise ValueError(f'Missing columns: {missing_columns}')

        users = []
        for index, row in df.iterrows():
            if row.isnull().any():
                raise ValueError(f'Null data at row {index + 1}')

            role = str(row['user_role']).strip()
            if role not in user_role:
                raise ValueError(f'Invalid role "{role}" at row {index + 1}')

            users.append({
                'fullname': str(row['fullname']).strip(),
                'username': str(row['username']).strip(),
                'email': str(row['email']).strip(),
                'password': str(row['cccd']).strip(),
                'user_role': role,
            })

        return users


admin.add_view(RoomView(Room, db.session, name='Phòng'))
admin.add_view(UserView(User, db.session, name='Tài khoản'))