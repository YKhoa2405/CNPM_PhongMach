
from datetime import datetime
from sqlalchemy import Column, String, Integer, Enum,Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from PhongMachApp import db, app
from flask_login import UserMixin
from enum import Enum as UserEnum

class Basemodel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

class UserRole(UserEnum):
    STAFF = 1
    USER = 2

class User(Basemodel, UserMixin):
    name = Column(String(50),nullable=False)
    email = Column(String(50),nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)

class DatLichKham(Basemodel):
    name = Column(String(50), nullable=False)
    cccd = Column(String(50), nullable=False, unique=True)
    gender = Column(String(10), nullable=False)
    sdt = Column(String(20), nullable=False, unique=True)
    birthday = Column(Date, nullable=False)
    address = Column(String(255), nullable=False)
    calendar = Column(Date, nullable=False)


class MedicineUnit(Basemodel):
    name = Column(String(30), unique=True, default='')
    medicines = relationship('Medicine', backref='medicine_unit', lazy=True)

    def __str__(self):
        return self.name


# Thuốc
class Medicine(Basemodel):
    name = Column(String(50), unique=True, default='', nullable=False)
    amount = Column(Integer, default=0)
    image = Column(String(255), nullable=True)
    import_date = Column(DateTime, default=datetime.now())
    expiration_date = Column(DateTime, default=datetime.now())
    component = Column(String(200), default='')
    price = Column(Integer, default=0.0)
    description = Column(String(500), default='')
    # # foreign keys
    medicineUnit_id = Column(Integer, ForeignKey(MedicineUnit.id), nullable=False)

    def __str__(self):
        return self.name


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
