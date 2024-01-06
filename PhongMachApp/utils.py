# Tuơng tác với csdl
from datetime import datetime

from flask import request, flash
from flask import session
from sqlalchemy import func, extract

from PhongMachApp import app, db, sms
from PhongMachApp.models import User, Medicine, MedicineUnit, Appointment, MedicalExamList, Prescription, PromissoryNote
import vonage
# Băm mật khẩu
import hashlib


def add_user(name, email, password, phone, **kwargs):
    # password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                email=email.strip(),
                phone=phone.strip(),
                password=password)
    db.session.add(user)
    db.session.commit()


def add_lich_kham(name, cccd, gender, sdt, birthday, address, calendar):
    # birthday = datetime.strptime(birthday, '%d-%m-%Y').date()
    # calendar = datetime.strptime(calendar, '%d-%m-%Y').date()
    datLichKham = Appointment(
        name=name.strip(),
        cccd=cccd.strip(),
        gender=gender.strip(),
        sdt=sdt.strip(),
        birthday=birthday,
        address=address.strip(),
        calendar=calendar)
    db.session.add(datLichKham)
    db.session.commit()


def check_login(email, password):
    if email and password:
        # password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return User.query.filter(User.email.__eq__(email.strip()),
                                 User.password.__eq__(password)).first()


def get_prev_url():
    referer = request.headers.get('Referer')

    if referer and referer != request.url:
        return referer
    else:
        return '/'


def load_medicineUnit():
    return MedicineUnit.query.all()


def load_medicine(kw=None, page=1):
    medicines_query = Medicine.query
    if kw:
        medicines_query = medicines_query.filter(Medicine.name.contains(kw))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size
    medicines = medicines_query.slice(start, end).all()

    return medicines


def count_medicine():
    return Medicine.query.count()


def get_email(user_email, ):
    return User.query.filter_by(email=user_email).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_medicine_by_id(medicine_id):
    return Medicine.query.get(medicine_id)


def count_cart(cart):
    total_quantity = 0
    total_amount = 0

    if cart:
        for c in cart.values():
            total_quantity += c.get('quantity', 0)

    return {
        'total_quantity': total_quantity
    }


# y tas
def get_patient_phone_number(patient_id):
    patient = Appointment.query.get(patient_id)
    if patient:
        return patient.sdt
    return None


def send_appointment_date_to_patient(patient_phone_number, appointment_date):
    message = (f"Phong kham HNK thong bao ngay kham benh cua ban la {appointment_date}.")

    # Gửi tin nhắn đến số điện thoại bệnh nhân
    response = sms.send_message({
        'from': 'Vonage APIs',
        'to': patient_phone_number,
        'text': message,
        'type': 'unicode'
    })

    if response['messages'][0]['status'] == '0':
        print(f"Message sent successfully to {patient_phone_number}.")
    else:
        print(f"Message to {patient_phone_number} failed with error: {response['messages'][0]['error-text']}")


def format_date(input_date):
    # Chuyển đổi ngày từ chuỗi "YYYY-MM-DD" sang đối tượng datetime
    formatted_date = datetime.strptime(input_date, "%Y-%m-%d")

    # Định dạng lại ngày thành "Ngày tháng Năm"
    result_date = formatted_date.strftime("%d-%m-%Y")

    return result_date


def get_patient_name(patient_id):
    patient = Appointment.query.filter_by(id=patient_id).first()
    return patient.name if patient else None


# bác sĩ

# lấy ngày khám hôm nay trong medical exam list
def get_medical_exams_by_date(target_date):
    medical_exams = MedicalExamList.query.join(Appointment, MedicalExamList.appointment_id == Appointment.id).filter(
        Appointment.calendar == target_date).all()
    return medical_exams


def get_patient_info(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    if appointment:
        return {'name': appointment.name, 'appointment_date': appointment.calendar, 'CCCD': appointment.cccd}
    return {'name': None, 'appointment_date': None, 'CCCD':None}


def get_unit_name_by_id(unit_id):
    unit = MedicineUnit.query.filter_by(id=unit_id).first()
    if unit:
        return unit.name
    return None


# thống kê, báo cáo
def medicines_stats(kw):
    m = db.session.query(Medicine.id, Medicine.name, func.sum(Prescription.quantity), func.sum(Prescription.use_number))\
        .join(Prescription, Prescription.medicine_id.__eq__(Medicine.id))\
        .group_by(Medicine.id, Medicine.name)

    if kw:
        m = m.filter(Medicine.name.contains(kw))

    return m.all()


def medical_stats(year):
    medi = db.session.query(
        func.extract('month', PromissoryNote.date),
        func.count(PromissoryNote.id)
    ).group_by(func.extract('month', PromissoryNote.date)).filter(extract('year', PromissoryNote.date).__eq__(year)).order_by(extract('month', PromissoryNote.date))

    return medi.all()


# def is_patient_quantity_exceeded(list_code, patient_quantity):
#     # Lấy số lượng bệnh nhân đã đăng kí trong danh sách mới
#     current_patient_count = MedicalExamList.query.filter_by(list_code=list_code).count()
#     return current_patient_count >= patient_quantity

def create_appointment(appointment_info):
    list_code = appointment_info.get('list_code')
    medical_exam_list = MedicalExamList.query.filter_by(list_code=list_code).first()

    if medical_exam_list.is_patient_quantity_exceeded():
        # Hiển thị thông báo không thể đăng ký cuộc hẹn do đủ số lượng bệnh nhân
        return flash(f"Không thể đăng ký cuộc hẹn vì đã đủ số lượng bệnh nhân trong danh sách khám này.")
