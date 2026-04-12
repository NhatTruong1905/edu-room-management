from flask import render_template
from eduroomapp import app


@app.route('/')
def index():
    return render_template("user.html")


@app.route('/login')
def login_view():
    return render_template('login.html')


@app.route('/register')
def register_view():
    return render_template('register.html')

@app.route('/admin')
def admin_view():
    return render_template("admin.html")

if __name__ == '__main__':
    app.run(debug=True)
