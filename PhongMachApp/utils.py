# Tuơng tác với csdl
from datetime import datetime
from PhongMachApp import app, db
from PhongMachApp.models import User, DatLichKham, Medicine, MedicineUnit
# Băm mật khẩu
import hashlib


def add_user(name, email, password, **kwargs):
    # password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                email=email.strip(),
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


def load_medicine(kw=None):
    medicines_query = Medicine.query
    if kw:
        medicines_query = medicines_query.filter(Medicine.name.contains(kw))

    medicines = medicines_query.all()

    return medicines


def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_medicine_by_id(medicine_id):
    return Medicine.query.get(medicine_id)
