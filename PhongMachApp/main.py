import math, re

import cloudinary.uploader
from flask import render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import login_user, logout_user
from sqlalchemy import func

from PhongMachApp.models import UserRole
from datetime import datetime, date
from PhongMachApp import app, utils, login, models, db
from PhongMachApp.models import UserRole, MedicalExamList, Appointment, Prescription, PromissoryNote, Regulation
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
        avatar_path = None

        if password.strip() == confirm.strip():

            # Check if email is in a valid format
            if not is_valid_email(email):
                err_msg = "Định dạng email không hợp lệ."
            else:
                # Check if the email is already registered
                if utils.get_email(email):
                    err_msg = "Email đã được đăng ký. Vui lòng chọn email khác."
                else:
                    avatar = request.files.get('avatar')
                    if avatar:
                        res = cloudinary.uploader.upload(avatar)
                        avatar_path = res['secure_url']
                    # Add the new user to the database
                    utils.add_user(name=name, email=email, password=password, phone=phone, avatar=avatar_path)
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
            session['name'] = user.name
            session['user_role'] = user.user_role.value
            if user.user_role == UserRole.DOCTOR:
                return redirect('doctor/patient_list')
            elif user.user_role == UserRole.NURSE:
                # Add the corresponding action for nurses, for example:
                return redirect('show_result')
            elif user.user_role == UserRole.CASHIER:
                # Add the corresponding action for nurses, for example:
                return redirect('cashier')
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


@app.route("/profile")
def profile():
    return render_template('profile.html')


@app.route("/datLichKham", methods=['get', 'post'])
def datLichKham():
    err_msg = ""
    err_msg1 = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        cccd = request.form.get('cccd')
        gender = request.form.get('optradio')
        sdt = request.form.get('sdt')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        calendar = request.form.get('calendar')

        try:
            existing_appointments_count = Appointment.query.filter_by(calendar=calendar).count()

            # Truy vấn giá trị patient_quantity từ bảng Regulation
            regulation = Regulation.query.first()
            max_appointments_allowed = regulation.patient_quantity

            if existing_appointments_count >= max_appointments_allowed:
                err_msg = "Lỗi đặt lịch! Đã đủ số lượng đăng kí khám"
            else:
                utils.add_lich_kham(name=name, cccd=cccd, gender=gender, sdt=sdt, birthday=birthday, address=address,
                                    calendar=calendar)
                err_msg = "Đặt lịch khám thành công!"
        except Exception as e:
            print(e)
<<<<<<< HEAD
            err_msg = "Đã xảy ra lỗi khi đặt lịch!"
    return render_template('datLichKham.html', err_msg=err_msg, current_page='datLichKham')
=======
            err_msg1 = "Đã xảy ra lỗi khi đặt lịch khám."
    return render_template('datLichKham.html', err_msg=err_msg, err_msg1=err_msg1, current_page='datLichKham')
>>>>>>> fc2ecb69077e8f6b5b355b8df7c3c42ff46ba06e


# Danh sách bệnh nhân khám theo ngày đươcj y tá lọc
@app.route('/doctor/patient_list')
def doctor_patient_list():
    today = date.today()  # Lấy ngày hiện tại
    # success= session.setdefault('success', False)
    medical_exams = utils.get_medical_exams_by_date(today)  # Lấy danh sách cuộc hẹn cho ngày hiện tại
    appointment_ids = [note.appointment_id for note in
                       PromissoryNote.query.all()]  # LẤY ID NHỮNG CUỘC HẸN RA ĐỂ CUSTOM BUTTON
    return render_template('doctor/patient_list.html', medical_exams=medical_exams, target_date=today,
                           appointment_ids=appointment_ids)


# Lap phieu kham
@app.route('/examination_form/<int:appointment_id>')
def examination_form(appointment_id):
    kwmedi = request.args.get('keywordmedi')
    medis = utils.load_medicine(kw=kwmedi)
    patient_info = utils.get_patient_info(appointment_id)
    return render_template('doctor/PhieuKham.html', kw=kwmedi, medicines=medis, name=patient_info['name'],
                           calendar=patient_info['appointment_date'], CCCD=patient_info['CCCD'],
                           appointment_id=appointment_id)


# Thêm thuốc
@app.route('/api/add_medicine', methods=['put'])
def add_medicine():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    medicineUnit_id = data.get('medicineUnit_id')

    cart = session.get('cart')
    if not cart:
        cart = {}
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'medicineUnit_id': medicineUnit_id,
            'medicine_unit_name': utils.get_unit_name_by_id(medicineUnit_id),
            'quantity': 1
        }
    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


# Xóa thuốc
@app.route('/api/delete_cart/<medicine_id>', methods=['delete'])
def delete_cart(medicine_id):
    cart = session.get('cart')

    if cart and medicine_id in cart:
        del cart[medicine_id]
        session['cart'] = cart
    return jsonify(utils.count_cart(cart))


# LẬP PHIẾU KHÁM
@app.route('/create_prescription', methods=['POST'])
def create_prescription():
    if request.method == 'POST':
        if current_user.is_authenticated:
            user_id = current_user.get_id()

            appointment_id = request.form.get('appointment_id')
            date = request.form.get('date')
            symptom = request.form.get('symptom')
            forecast = request.form.get('forecast')
            CCCD = request.form.get('CCCD')
            new_prescription = PromissoryNote(
                date=date,
                symptom=symptom,
                forecast=forecast,
                appointment_id=appointment_id,
                user_id=user_id,
                CCCD=CCCD
            )

            db.session.add(new_prescription)
            db.session.commit()

            medicine_list = []  # Tạo danh sách Prescription để thêm vào session

            medicine_ids = request.form.getlist('id_medi')
            medicine_quantities = request.form.getlist('count_medi')
            usages = request.form.getlist('usage')

            for i in range(len(medicine_ids)):
                medicine = Medicine.query.get(medicine_ids[i])
                if medicine:
                    prescription = Prescription(
                        promissory_id=new_prescription.id,
                        medicine_id=medicine_ids[i],
                        quantity=medicine_quantities[i],
                        usage_detail=usages[i],
                        use_number=1
                    )
                    medicine_list.append(prescription)

            # Thêm tất cả các Prescription vào session cùng một lúc
            db.session.add_all(medicine_list)
            db.session.commit()  # Commit sau khi thêm tất cả các Prescription vào session

            session['success'] = True
            session.pop('cart', None)
        flash(f'LẬP PHIẾU KHÁM THÀNH CÔNG!!!!', 'success')
        return redirect('/doctor/patient_list')


# lịch sử khám
@app.route('/fetch_medical_history', methods=['POST'])
def fetch_medical_history():
    cccd = request.form.get('cccd')
    # Truy vấn cơ sở dữ liệu để lấy lịch sử khám bệnh dựa trên CCCD
    medical_history = PromissoryNote.query.filter_by(CCCD=cccd).all()
    # Chuyển đổi kết quả thành dạng JSON và trả về cho frontend
    result = []
    for history in medical_history:
        result.append({
            'date': history.date,
            'symptom': history.symptom,
            'forecast': history.forecast
        })
    return jsonify(result)


# HIỂN THỊ DANH SÁCH BỆNH NHÂN ĐK
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

        # Kiểm tra số lượng lịch hẹn cho ngày đã chọn
        existing_appointments_count = Appointment.query.filter_by(calendar=calendar).count()

        # Truy vấn giá trị patient_quantity từ bảng Regulation
        regulation = Regulation.query.first()
        max_appointments_allowed = regulation.patient_quantity

        if existing_appointments_count >= max_appointments_allowed:
            flash('Đã đủ số lượng khám bệnh cho ngày này. Vui lòng chọn ngày khác.', 'danger')
            return redirect(url_for('show_result'))

        # Thêm lịch hẹn mới vào cơ sở dữ liệu
        db.session.add(new_appointment)
        db.session.commit()
        flash('Thêm thông tin khám bệnh nhân thành công', 'success')
        return redirect(url_for('show_result'))



@app.route('/show_result')
def show_result():
    appointments = Appointment.query.all()
    appointment_list = MedicalExamList.query.all()  # Danh sách đã lập
    filtered_appointments = [appointment for appointment in appointments if
                             appointment.id not in [item.appointment_id for item in appointment_list]]
    return render_template('nurse/patient_list.html', appointments=filtered_appointments)


# xóa bệnh nhân khỏi db
@app.route('/patients/<int:appointment_id>/delete', methods=['POST'])
def delete_patient(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    appointments = Appointment.query.all()
    # new_id = 1
    #
    # for appoinment in appointments:
    #     appoinment.id = new_id
    #     new_id += 1

    db.session.commit()
    return flash('Xóa bệnh nhân thành công', 'success')


# lọc bệnh nhân theo ngày khám
@app.route('/get_patients_by_date', methods=['GET'])
def get_patients_by_date():
    selected_date = request.args.get('ngayKham')

    # Danh sách bệnh nhân đã có trong MedicalExamList
    appointments_in_list = [medical_exam.appointment_id for medical_exam in
                            MedicalExamList.query.filter_by(appointment_date=selected_date).all()]

    # Lọc danh sách các bệnh nhân chưa có trong danh sách khám
    appointments = Appointment.query.filter_by(calendar=selected_date).all()
    appointments_not_in_list = [appointment for appointment in appointments if
                                appointment.id not in appointments_in_list]

    appointment_count = len(appointments_not_in_list)

    if appointment_count == 0:
        flash('Không có bệnh nhân đăng ký lịch khám vào ngày này !!!', 'danger')
        return redirect(url_for('show_result'))

    # Lưu danh sách bệnh nhân vào session
    session['selected_patients'] = [appointment.id for appointment in appointments_not_in_list]

    return render_template('nurse/patient_list_by_date.html', appointments=appointments_not_in_list,
                           appointment_count=appointment_count, selected_date=selected_date)


# lập danh sách khám
@app.route('/appointment_list', methods=['POST'])
def create_appointment_list():
    # Lấy danh sách bệnh nhân đã được chọn từ session
    selected_patients = session.get('selected_patients', [])
    # Lấy ID ca khám cuối cùng trong bảng MedicalExamList
    latest_count = db.session.query(func.max(MedicalExamList.list_code)).scalar() or 0
    new_count = int(latest_count) + 1
    list_code = new_count
    # Lấy ngày khám từ form
    appointment_date = request.form.get('appointment_date')
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        if appointment_date:
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
                    # patient_phone_number = utils.get_patient_phone_number(patient_id)
                    # utils.send_appointment_date_to_patient(patient_phone_number, appointment_date)
            db.session.commit()
            session.pop('selected_patients', None)

            # Hiển thị danh sách đã lập
            new_appointments = MedicalExamList.query.filter_by(appointment_date=appointment_date).all()
            return render_template('nurse/appointment_list.html', appointments=new_appointments,
                                   appointment_date=utils.format_date(appointment_date), appointment_code=list_code)
        return 'Lập danh sách không thành công'


#  thu ngân
@app.route("/cashier")
def cashier_home():
    all_notes = PromissoryNote.query.all()  # truy vấn phiếu khám
    # prescriptions = Prescription.query.all()#truy phấn phiếu thuôcs
    return render_template('cashier/cashier_home.html', all_notes=all_notes)


@app.route("/cashier/pay_bill")
def pay_bill():
    return render_template('cashier/pay_bill.html')


# admin
@app.route('/admin/signin_admin', methods=['post'])
def signin_admin():
    email = request.form.get('email')
    password = request.form.get('password')

    user = utils.check_login(email=email, password=password)
    if user:
        login_user(user=user)
    return redirect(utils.get_prev_url())


####

if __name__ == '__main__':
    from PhongMachApp.admin import *

    app.run(debug=True, port=5000)
