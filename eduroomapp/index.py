from flask import render_template, request, redirect
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
    return render_template('index.html')


@app.route('/login')
def login_view():
    return render_template('login.html')


@app.route('/register')
def register_view():
    return render_template('register.html')


@app.route('/register', methods=['post'])
def register_process():
    data = request.form

    password = data.get('password')
    confirm = data.get('confirm')
    if password != confirm:
        err_msg = 'Mật khẩu không khớp!'
        return render_template('register.html', err_msg=err_msg)

    try:
        add_user(fullname=data.get('fullname'), username=data.get('username'), password=password)
        return redirect('/login')
    except ValueError as ex:
        return render_template('register.html', err_msg=str(ex))
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex))


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
            return "Vui lòng nhập đầy đủ tài khoản và mật khẩu!"

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            next = request.args.get('next')
            return redirect(next if next else '/')
        else:
            return "Tài khoản hoặc mật khẩu không chính xác!"

    return render_template('login.html')


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)


# @app.route('/admin')
# def admin_view():
#     return render_template("admin.html")


if __name__ == '__main__':
    app.run(debug=True)
