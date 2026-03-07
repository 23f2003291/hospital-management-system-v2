from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # admin / doctor / patient

    doctor = db.relationship('Doctor', backref='user', uselist=False)
    patient = db.relationship('Patient', backref='user', uselist=False)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))

    doctors = db.relationship('Doctor', backref='department')


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    name = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    availability = db.Column(db.String(200))

    appointments = db.relationship('Appointment', backref='doctor')


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))

    appointments = db.relationship('Appointment', backref='patient')


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))

    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    status = db.Column(db.String(20))  # booked / completed / cancelled

    treatment = db.relationship('Treatment', backref='appointment', uselist=False)


class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))

    diagnosis = db.Column(db.String(200))
    prescription = db.Column(db.String(200))
    notes = db.Column(db.String(200))