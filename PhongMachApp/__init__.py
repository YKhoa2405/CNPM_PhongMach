from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
import cloudinary

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:%s@localhost/phongmachdb?charset=utf8mb4" % quote('Caichyrua11@')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db =SQLAlchemy(app=app)
# admin = Admin(app=app, name='QUẢN LÝ PHÒNG MẠCH', template_mode='bootstrap4')

login = LoginManager(app=app)


cloudinary.config(
    cloud_name="dsbebvfff",
    api_key="825956681133294",
    api_secret="mlg4G6x3cLisjUC_sKx4GiGpYQk"
)
