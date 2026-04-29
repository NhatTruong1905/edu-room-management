from datetime import datetime

import pandas as pd
import hashlib
import bcrypt
from flask import request, redirect, url_for, flash
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from eduroomapp.models import UserRole, Room, User, Booking, BookingStatus
from eduroomapp import admin, db


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
    column_labels = {
        'id': 'Mã phòng',
        'name': 'Tên phòng',
        'capacity': 'Sức chứa'
    }

    def delete_model(self, model):
        future_booking = Booking.query.filter(
            Booking.room_id == model.id,
            Booking.start_time > datetime.now(),
            Booking.status == BookingStatus.CONFIRMED
        ).first()

        if future_booking:
            flash('Không thể xóa phòng vì đã có lịch đặt trong tương lai!', 'error')
            return False

        return super().delete_model(model)


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

        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        count = 0
        for _, row in df.iterrows():
            username = str(row['username']).strip()
            cccd = str(row['cccd']).strip()
            byte_password = cccd.encode('utf-8')
            hash_password = bcrypt.hashpw(byte_password, bcrypt.gensalt(12))
            password = hash_password.decode('utf-8')
            user = User(
                fullname=str(row['fullname']).strip(),
                username=username,
                email=str(row['email']).strip() if pd.notna(row['email']) else None,
                password=password,
                user_role=UserRole[str(row['user_role']).strip()]
            )
            db.session.add(user)
            count += 1

        db.session.commit()
        flash(f"Thêm thành công {count} tài khoản", "success")

        return redirect(url_for('.index_view'))

    @expose('/import-csv', methods=['GET'])
    def import_csv_view(self):
        return self.render('admin/import_csv_view.html')


admin.add_view(RoomView(Room, db.session, name='Phòng'))
admin.add_view(UserView(User, db.session, name='Tài khoản'))
