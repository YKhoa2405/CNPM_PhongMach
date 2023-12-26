
from PhongMachApp import app, utils, login, models
from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from PhongMachApp.models import UserRole

app.secret_key = 'Caichyrua11@'

@app.route("/")
def index():

    kwmedi = request.args.get('keywordmedi')
    medis = utils.load_medicine(kw=kwmedi)
    return render_template('index.html', medicines=medis)

# @app.route("/doctor")
# def doctor():
#
#     return render_template('doctor/doctor.html', )
@app.route('/medicines/<int:medicine_id>')
def medicine_detail(medicine_id):
    medicine = utils.get_medicine_by_id(medicine_id)
    return render_template('medicine_detail.html', medicine=medicine)


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password.strip().__eq__(confirm.strip()):
            utils.add_user(name=name, email=email, password=password)
            return redirect(url_for('user_login'))
        else:
            err_msg = "Mật khẩu và xác nhận mật khẩu không khớp."
    return render_template('register.html', err_msg=err_msg)


@app.route('/login', methods=['get', 'post'])
def user_login():
    err_msg = ""
    if request.method.__eq__('POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        user = utils.check_login(email=email, password=password)
        if user:
            login_user(user=user)
            if user.user_role == UserRole.STAFF:
                return render_template('doctor/doctor.html')
            else:
                return redirect(url_for('index'))

        else:
            err_msg = "Email hoặc mật khẩu không chính xác."

    return render_template('login.html', err_msg=err_msg)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)

@app.route("/datLichKham",  methods=['get', 'post'])
def datLichKham():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        cccd = request.form.get('cccd')
        gender = request.form.get('optradio')
        sdt = request.form.get('sdt')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        calendar = request.form.get('calendar')

        try:
            utils.add_lich_kham(name=name, cccd=cccd, gender=gender, sdt=sdt, birthday=birthday, address=address, calendar=calendar)
            err_msg = "Đặt lịch khám thành công!"
        except Exception as e:
            print(e)
            err_msg = "Đã xảy ra lỗi khi đặt lịch khám."
    return render_template('datLichKham.html', err_msg=err_msg)

if __name__ == '__main__':
    from PhongMachApp.admin import *

    app.run(debug=True)