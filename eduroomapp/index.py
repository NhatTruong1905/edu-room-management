import math
from datetime import datetime, date, timedelta

from flask import render_template, request, redirect, flash, jsonify
from eduroomapp import app, dao
from flask_login import login_user, logout_user, login_required, current_user
from eduroomapp import login
from eduroomapp.dao import add_user


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/booking')
@login_required
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
    if password != confirm:
        err_msg = 'Xác nhận mật khẩu không khớp!'
        return render_template('register.html', err_msg=err_msg, roles=roles)

    try:
        add_user(fullname=data.get('fullname'), username=data.get('username'), password=password,
                 user_role=data.get('role'))

        flash('Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
        return redirect('/login')
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
    except ValueError:
        return jsonify({"error": "Định dạng ngày giờ không hợp lệ!"}), 400


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

    bookings_list = []
    for b in bookings:
        bookings_list.append({
            "id": b.id,
            "date": b.start_time.strftime('%d/%m/%Y'),
            "time_range": f"{b.start_time.strftime('%H:%M')} - {b.end_time.strftime('%H:%M')}",
            "capacity": b.room.capacity,
            "status": b.status.name,
            "name_room": b.room.name
        })

    return jsonify({"bookings": bookings_list}), 200


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)


# @app.route('/admin')
# def admin_view():
#     return render_template("admin.html")


if __name__ == '__main__':
    app.run(debug=True)
