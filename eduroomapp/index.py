import math
from datetime import datetime, date, timedelta
import os
from flask import render_template, request, redirect, flash, jsonify, url_for
from eduroomapp import app, dao, google, db, facebook
from flask_login import login_user, logout_user, login_required, current_user
from eduroomapp import login
from eduroomapp.dao import add_user
from eduroomapp.models import UserRole
from eduroomapp.utils import permission


def register_root(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/booking')
    @permission(allow={"roles": [UserRole.ADMIN], "access": False})
    def booking_dashboard():
        today = date.today()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)

        today_bookings = dao.get_booking_count_today(current_user.id, today)
        week_bookings = dao.get_booking_count_week(current_user.id, start_week, end_week)
        week_cancels = dao.get_cancel_count_week(current_user.id, start_week, end_week)

        return render_template('booking.html',
                               today_bookings=today_bookings,
                               week_bookings=week_bookings,
                               week_cancels=week_cancels)

    @app.route('/login')
    def login_view():
        return render_template('login.html')

    @app.route('/login/google')
    def login_google():
        redirect_uri = url_for('authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)

    @app.route('/login/facebook')
    def login_facebook():
        redirect_uri = url_for('authorize_facebook', _external=True)
        return facebook.authorize_redirect(redirect_uri)

    @app.route('/authorize/google')
    def authorize_google():
        try:
            token = google.authorize_access_token()
            user_info = token.get('userinfo')
        except Exception as e:
            flash('Đăng nhập Google thất bại hoặc đã bị hủy!', 'danger')
            return redirect('/login')

        google_email = user_info.get('email')
        google_name = user_info.get('name')

        user = dao.get_user_by_email(google_email)

        if not user:
            try:
                user = dao.create_user_from_google(google_email, google_name)
            except Exception as e:
                flash('Lỗi khi tạo tài khoản từ Google!', 'danger')
                return redirect('/login')

        login_user(user)
        flash(f'Xin chào {user.fullname}, bạn đã đăng nhập thành công!', 'success')
        return redirect('/')

    @app.route('/authorize/facebook')
    def authorize_facebook():
        try:
            token = facebook.authorize_access_token()
            resp = facebook.get('me?fields=id,name,email')
            user_info = resp.json()
        except Exception as e:
            flash('Đăng nhập Facebook thất bại hoặc đã bị hủy!', 'danger')
            return redirect('/login')

        facebook_id = user_info.get('id')
        facebook_name = user_info.get('name')
        facebook_email = user_info.get('email')

        user = None
        if facebook_email:
            user = dao.get_user_by_email(facebook_email)
        else:
            username_fb = f"fb_{facebook_id}"
            user = dao.get_user_by_username(username_fb)

        if not user:
            try:
                user = dao.create_user_from_facebook(facebook_id, facebook_name, facebook_email)
            except Exception as e:
                flash('Lỗi khi tạo tài khoản từ Facebook!', 'danger')
                return redirect('/login')

        login_user(user)
        flash(f'Xin chào {user.fullname}, bạn đã đăng nhập thành công!', 'success')
        return redirect('/')

    @app.route('/register')
    def register_view():
        roles = dao.get_user_role()
        return render_template('register.html', roles=roles)

    @app.route('/register', methods=['post'])
    def register_process():
        roles = dao.get_user_role()
        data = request.form

        password = data.get('password')
        confirm = data.get('confirm_password')
        email = data.get('email')
        if password != confirm:
            err_msg = 'Xác nhận mật khẩu không khớp!'
            return render_template('register.html', err_msg=err_msg, roles=roles)

        try:
            add_user(fullname=data.get('fullname'),
                     username=data.get('username'),
                     password=password,
                     user_role=data.get('role'),
                     email=email)

            flash('Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
            return redirect('/login')
        except ValueError as ex:
            return render_template('register.html', err_msg=str(ex), roles=roles)
        except Exception as ex:
            return render_template('register.html', err_msg=str(ex), roles=roles)

    @app.route('/logout')
    def logout_process():
        logout_user()
        return redirect('/login')

    @app.route('/login', methods=['POST', 'GET'])
    def login_process():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                err_msg = "Vui lòng nhập đầy đủ tài khoản và mật khẩu!"
                return render_template('login.html', err_msg=err_msg)

            user = dao.auth_user(username=username, password=password)
            if user:
                login_user(user=user)
                next = request.args.get('next')
                return redirect(next if next else '/')
            else:
                err_msg = "Tài khoản hoặc mật khẩu không chính xác!"
                return render_template('login.html', err_msg=err_msg)

        return render_template('login.html')

    @app.route('/api/rooms', methods=['GET'])
    def api_get_rooms():
        date_str = request.args.get('date')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        capacity = request.args.get('capacity')
        page = request.args.get('page', 1, type=int)

        if not (date_str and start_time_str and end_time_str):
            return jsonify({"error": "Vui lòng chọn đầy đủ ngày và giờ"}), 400

        try:
            start_time = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")

            rooms, total_count = dao.get_rooms_by_date_and_time(start_time, end_time, capacity, page)

            total_pages = math.ceil(total_count / app.config["PAGE_SIZE"])
            room_list = []
            for r, is_booked in rooms:
                if is_booked:
                    final_status = "BOOKED"
                elif r.status.name == "MAINTENANCE":
                    final_status = "MAINTENANCE"
                else:
                    final_status = "AVAILABLE"

                room_list.append({
                    "id": r.id,
                    "name": r.name,
                    "capacity": r.capacity,
                    "status": final_status
                })

            return jsonify({
                "rooms": room_list,
                "total_pages": total_pages,
                "current_page": page,
                "total_count": total_count
            }), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "Đã xảy ra lỗi hệ thống!"}), 400

    @app.route('/api/bookings', methods=['POST'])
    @login_required
    def api_create_booking():
        room_id = request.form.get('room_id')
        date_str = request.form.get('booking_date')
        start_str = request.form.get('booking_start_time')
        end_str = request.form.get('booking_end_time')

        if not all([room_id, date_str, start_str, end_str]):
            flash('Lỗi: Thiếu thông tin đặt phòng!', 'danger')
            return redirect('/booking')

        if current_user.locked_until and current_user.locked_until > datetime.now():
            flash('Tài khoản của bạn đang bị khóa quyền đặt phòng do hủy quá nhiều lần!', 'danger')
            return redirect('/booking')

        try:
            start_dt = datetime.strptime(f"{date_str} {start_str}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date_str} {end_str}", "%Y-%m-%d %H:%M")

            booking_date = start_dt.date()
            count_booking_today = dao.get_booking_count_today(user_id=current_user.id, today_date=booking_date)
            if count_booking_today >= 3:
                flash('Đã giới hạn đặt quá 3 phòng / ngày!', 'warning')
                return redirect('/booking')

            start_week = booking_date - timedelta(days=booking_date.weekday())
            end_week = start_week + timedelta(days=6)
            count_booking_week = dao.get_booking_count_week(user_id=current_user.id,
                                                            start_week=start_week,
                                                            end_week=end_week)
            if count_booking_week >= 10:
                flash('Đã giới hạn quá 10 phòng / tuần!', 'warning')
                return redirect('/booking')

            dao.add_booking(
                user_id=current_user.id,
                room_id=room_id,
                start_time=start_dt,
                end_time=end_dt
            )

            flash('Đặt phòng thành công!', 'success')
        except Exception as ex:
            flash(f'Đặt phòng thất bại. Vui lòng thử lại! \n Lỗi: {str(ex)}', 'danger')
        return redirect('/booking')

    @app.route('/api/bookings', methods=['GET'])
    @login_required
    def api_get_bookings():
        bookings = dao.get_bookings_user(user_id=current_user.id)
        now = datetime.now()

        bookings_list = []
        for b in bookings:
            if b.status.name == 'CANCELED':
                display_status = 'CANCELED'
            elif b.end_time < now:
                display_status = 'COMPLETED'
            elif b.start_time <= now <= b.end_time:
                display_status = 'ONGOING'
            else:
                display_status = 'UPCOMING'
            bookings_list.append({
                "id": b.id,
                "date": b.start_time.strftime('%d/%m/%Y'),
                "time_range": f"{b.start_time.strftime('%H:%M')} - {b.end_time.strftime('%H:%M')}",
                "capacity": b.room.capacity,
                "status": display_status,
                "name_room": b.room.name
            })

        return jsonify({"bookings": bookings_list}), 200

    @app.route('/api/bookings/<int:id>', methods=['POST'])
    @permission(allow={"roles": [UserRole.STUDENT, UserRole.TEACHER], "access": True})
    def api_cancel_booking(id):
        try:
            dao.cancel_booking(booking_id=id, user_id=current_user.id)
            return jsonify({"success": True, "message": "Hủy phòng thành công!"}), 200
        except Exception as ex:
            return jsonify({"success": False, "message": str(ex)}), 400


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)


# @app.route('/admin')
# def admin_view():
#     return render_template("admin.html")


if __name__ == '__main__':
    register_root(app=app)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='localhost', port=5000, debug=True)
