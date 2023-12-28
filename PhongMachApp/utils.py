# Tuơng tác với csdl
from datetime import datetime
from PhongMachApp import app, db
from PhongMachApp.models import User, DatLichKham, Medicine, MedicineUnit
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
    datLichKham = DatLichKham(
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


def load_medicineUnit():
    return MedicineUnit.query.all()


def load_medicine(kw=None, page=1):
    medicines_query = Medicine.query
    if kw:
        medicines_query = medicines_query.filter(Medicine.name.contains(kw))

    page_size = app.config['PAGE_SIZE']
    start = (page-1)*page_size
    end = start + page_size
    medicines = medicines_query.slice(start, end).all()

    return medicines

def count_medicine():
    return Medicine.query.count()


def get_email(user_email,):
    return User.query.filter_by(email=user_email).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_medicine_by_id(medicine_id):
    return Medicine.query.get(medicine_id)
