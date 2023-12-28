import math
import re
from flask import render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import login_user, logout_user
from sqlalchemy import func

from PhongMachApp.models import UserRole
from datetime import datetime
from PhongMachApp import app, utils, login, models, db
from PhongMachApp.models import UserRole, MedicalExamList, Appointment
from flask import make_response

app.secret_key = 'Caichyrua11@'


@app.route("/")
def index():
    kwmedi = request.args.get('keywordmedi')
    page = request.args.get('page', 1)
    medis = utils.load_medicine(kw=kwmedi, page=int(page))
    countmedi = utils.count_medicine()
    return render_template('index.html', medicines=medis, current_page='index',
                           pages=math.ceil(countmedi / app.config['PAGE_SIZE']))


# Thuoc, danh muc thuoc
@app.route('/medicines/<int:medicine_id>')
def medicine_detail(medicine_id):
    medicine = utils.get_medicine_by_id(medicine_id)
    return render_template('medicine_detail.html', medicine=medicine)


# kiem tra dinh dang email
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password.strip() == confirm.strip():
            # Check if email is in a valid format
            if not is_valid_email(email):
                err_msg = "Định dạng email không hợp lệ."
            else:
                # Check if the email is already registered
                if utils.get_email(email):
                    err_msg = "Email đã được đăng ký. Vui lòng chọn email khác."
                else:
                    # Add the new user to the database
                    utils.add_user(name=name, email=email, password=password, phone=phone)
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


@app.route("/datLichKham", methods=['get', 'post'])
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
            utils.add_lich_kham(name=name, cccd=cccd, gender=gender, sdt=sdt, birthday=birthday, address=address,
                                calendar=calendar)
            err_msg = "Đặt lịch khám thành công!"
        except Exception as e:
            print(e)
            err_msg = "Đã xảy ra lỗi khi đặt lịch khám."
    return render_template('datLichKham.html', err_msg=err_msg, current_page='datLichKham')


@app.route('/lapPhieuKham')
def lapPhieuKham():
    kwmedi = request.args.get('keywordmedi')
    medis = utils.load_medicine(kw=kwmedi)
    return render_template('doctor/lapPhieuKham.html', kw=kwmedi, medicines=medis)


@app.route('/api/add_medicine', methods=['POST'])
def add_medicine():
    data = request.json  # Assuming you're sending data in JSON format

    # Extracting data from the request
    id = data.get('id')
    name = data.get('name')
    medicine_unit = data.get('medicine_unit')

    # Retrieving the cart from the session
    cart = session.get('cart', {})

    # Checking if the id is already in the cart
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'medicine_unit': medicine_unit,
            'quantity': 1
        }

    # Updating the cart in the session
    session['cart'] = cart

    return jsonify({'message': 'Medicine added to cart successfully'})


######################## Y TA --------------------------------------

# trang y tá
@app.route("/nurse")
def nurse_home():
    return render_template('nurse/nurse_home.html')


@app.route('/result', methods=['POST', 'GET'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        cccd = request.form['cccd']
        gender = request.form['optradio']
        sdt = request.form['sdt']
        birthday = request.form['birthday']
        address = request.form['address']
        calendar = request.form['calendar']

        new_appointment = Appointment(
            name=name,
            cccd=cccd,
            gender=gender,
            sdt=sdt,
            birthday=birthday,
            address=address,
            calendar=calendar
        )

        # Thêm bệnh nhân mới vào cơ sở dữ liệu
        db.session.add(new_appointment)
        db.session.commit()

        # Lấy danh sách bệnh nhân từ cơ sở dữ liệu
        appointments = Appointment.query.all()

        # Cập nhật lại ID cho từng bệnh nhân
        new_id = 1
        for appoinment in appointments:
            appoinment.id = new_id
            new_id += 1

    db.session.commit()
    flash('THÊM THÔNG TIN KHÁM BỆNH NHÂN THÀNH CÔNG', 'success')
    return redirect(url_for('show_result'))


# Route hiển thị danh sách bệnh nhân
@app.route('/show_result')
def show_result():
    appointments = Appointment.query.all()
    return render_template('nurse/patient_list.html', appointments=appointments)


# xóa bệnh nhân
@app.route('/patients/<int:appointment_id>/delete', methods=['POST'])
def delete_patient(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    appointments = Appointment.query.all()
    new_id = 1

    for appoinment in appointments:
        appoinment.id = new_id
        new_id += 1

    db.session.commit()
    return flash('Xóa bệnh nhân thành công', 'success')


# lọc bệnh nhân theo ngày khám
@app.route('/get_patients_by_date', methods=['GET'])
def get_patients_by_date():
    selected_date = request.args.get('ngayKham')
    appointments = Appointment.query.filter_by(calendar=selected_date).all()
    appointment_count = len(appointments)
    # Lưu danh sách bệnh nhân vào session
    session['selected_patients'] = [appointment.id for appointment in appointments]

    return render_template('nurse/patient_list_by_date.html', appointments=appointments,
                           appointment_count=appointment_count)


# lập ds khám
@app.route('/appointment_list', methods=['POST'])
def create_appointment_list(user_id=1):
    # Lấy danh sách bệnh nhân đã được chọn từ session
    selected_patients = session.get('selected_patients', [])
    # Lấy ID ca khám cuối cùng trong bảng MedicalExamList
    latest_appointment = db.session.query(func.max(MedicalExamList.id)).scalar() or 0
    new_appointment_id = latest_appointment + 1
    # Lấy ngày khám từ form
    appointment_date = request.form.get('appointment_date')
    if appointment_date:
        list_code = str(new_appointment_id)
        for patient_id in selected_patients:
            # Kiểm tra xem bệnh nhân đã có lịch hẹn trong danh sách khám hay chưa
            existing_appointment = MedicalExamList.query.filter_by(appointment_id=patient_id).first()

            if existing_appointment:
                flash(
                    f'Lịch hẹn của bệnh nhân {utils.get_patient_name(patient_id)} đã được lập danh sách.Vui lòng lập danh sách những bệnh nhân khác!!',
                    'danger')
                return redirect(url_for('get_patients_by_date', ngayKham=appointment_date))
            else:
                # Nếu chưa có, thực hiện lưu thông tin
                person = MedicalExamList(
                    list_code=list_code,
                    created_date=datetime.now().date(),
                    appointment_date=appointment_date,
                    user_id=user_id,
                    appointment_id=patient_id
                )
                db.session.add(person)

                # Cập nhật trạng thái has_appointment_list của bệnh nhân

                # Gửi tin nhắn thông báo đến bệnh nhân (uncomment nếu cần)
                patient_phone_number = utils.get_patient_phone_number(patient_id)
                utils.send_appointment_date_to_patient(patient_phone_number, appointment_date)

        db.session.commit()
        session.pop('selected_patients', None)

        # Hiển thị danh sách đã lập
        new_appointments = MedicalExamList.query.filter_by(appointment_date=appointment_date).all()
        return render_template('nurse/appointment_list.html', appointments=new_appointments,
                               appointment_date=utils.format_date(appointment_date),appointment_code=list_code)

    return 'Lập danh sách không thành công'

if __name__ == '__main__':
    from PhongMachApp.admin import *

    app.run(debug=True)
