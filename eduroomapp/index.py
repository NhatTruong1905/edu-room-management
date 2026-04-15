import math
from datetime import datetime

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
    return render_template('booking.html')


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

        page_size = app.config.get("PAGE_SIZE", 6)
        total_pages = math.ceil(total_count / page_size)
        room_list = []
        for r in rooms:
            room_list.append({
                "id": r.id,
                "name": r.name,
                "capacity": r.capacity,
                "status": r.status.name
            })

        return jsonify({
            "rooms": room_list,
            "total_pages": total_pages,
            "current_page": page,
            "total_count": total_count
        }), 200

    except ValueError:
        return jsonify({"error": "Định dạng ngày giờ không hợp lệ!"}), 400


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)


# @app.route('/admin')
# def admin_view():
#     return render_template("admin.html")


if __name__ == '__main__':
    app.run(debug=True)
