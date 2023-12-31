from datetime import datetime
from sqlalchemy import Column, String, Integer, Enum, Float, ForeignKey, Date, DateTime, Table
from sqlalchemy.orm import relationship
from PhongMachApp import db, app
from flask_login import UserMixin
from enum import Enum as UserEnum


class Basemodel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    CASHIER = 5
    DOCTOR = 4
    NURSE = 2
    ADMIN = 3
    USER = 1


class User(Basemodel, UserMixin):
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False, unique=True)
    user_role = Column(Enum(UserRole), default=UserRole.USER)


Promissory_medicine = db.Table(  # CHI TIẾT PHIẾU THUỐC # bangr trung gian thuốc và phiếu khám
    'promissory_medicine',
    db.Column('id', Integer, primary_key=True, autoincrement=True),
    db.Column('promissory_id', Integer, ForeignKey('promissory_note.id'), primary_key=True),
    db.Column('medicine_id', db.Integer, db.ForeignKey('medicine.id'), primary_key=True),
    db.Column('quantiny', db.Integer),  # số lượng
    db.Column('use_number', db.Integer),  # số lần dùng
    db.Column('usage_detail', db.String(255)))


class Promissory_note(Basemodel):  # Phiếu khám
    date = Column(Date, nullable=False)  # ngày khám
    symptom = Column(String(100), nullable=False)  # triệu chứng
    forecast = Column(String(100), nullable=False)  # chẩn đoán
    appointment_id = Column(Integer, ForeignKey('appointment.id'))  # ID của lịch hẹn
    user_id = Column(Integer, ForeignKey('user.id'))  # ID của người lập phiếu
    medicines = relationship('Medicine', secondary=Promissory_medicine, backref='promissory_note', lazy=True)


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
    description = Column(String(1000), default='')
    # # foreign keys
    medicineUnit_id = Column(Integer, ForeignKey(MedicineUnit.id), nullable=False)

    def __str__(self):
        return self.name


class Appointment(Basemodel):  # LỊCH HẸN
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    cccd = db.Column(db.String(50), nullable=False, unique=True)
    gender = db.Column(db.String(10), nullable=False)
    sdt = db.Column(db.String(20), nullable=False, unique=True)
    birthday = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    calendar = db.Column(db.Date, nullable=False)
    medical_exam_lists = db.relationship('MedicalExamList',
                                         back_populates='appointment')  # Quan hệ với bảng MedicalExamList


# Danh sách khám gửi cho bác sĩ
class MedicalExamList(db.Model):  # Appointment list
    __tablename__ = 'medical_exam_list'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_code = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.Date, default=datetime.now().date())
    appointment_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Khóa ngoại tới bảng User
    user = db.relationship('User', backref='medical_exam_lists')  # Quan hệ với bảng User
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))  # Khóa ngoại mã cuộc hẹn
    appointment = db.relationship('Appointment', back_populates='medical_exam_lists')


# Hóa đơn


# amin quy dinh
class Regulation(Basemodel):
    patient_quantity = Column(Integer, default=40)
    examination_fee = Column(Float, default=100000)

    def __str__(self):
        return self.name


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
