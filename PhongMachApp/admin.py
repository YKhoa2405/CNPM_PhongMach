from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from PhongMachApp import app, db
from flask_admin.contrib.sqla import ModelView
from PhongMachApp.models import (User, DatLichKham, MedicineUnit, Medicine)


admin = Admin(app=app, name='PhongMach Administration', template_mode='bootstrap4')


class MedicineUnitView(ModelView):
    column_list = ['name', 'medicines']


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(DatLichKham, db.session))
admin.add_view(MedicineUnitView(MedicineUnit, db.session))
admin.add_view(ModelView(Medicine, db.session))
