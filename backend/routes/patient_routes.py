from flask import Blueprint, jsonify, request
from models import db, Doctor, Patient, Appointment, Treatment, Department
from redis_cache import get_cache, set_cache
from datetime import datetime

patient = Blueprint("patient", __name__)


# View doctors / search
@patient.route("/patient/doctors", methods=["GET"])
def view_doctors():

    name = request.args.get("name")
    specialization = request.args.get("specialization")

    cache_key = f"doctor_search_{name}_{specialization}"

    cached_data = get_cache(cache_key)

    if cached_data:
        return jsonify(cached_data)

    query = Doctor.query

    if name:
        query = query.filter(Doctor.name.ilike(f"%{name}%"))

    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))

    doctors = query.all()

    result = []

    for d in doctors:
        result.append({
            "doctor_id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "availability": d.availability
        })

    set_cache(cache_key, result, expiry=60)

    return jsonify(result)

# Book appointment
@patient.route("/patient/book_appointment", methods=["POST"])
def book_appointment():

    data = request.json

    doctor_id = data["doctor_id"]
    patient_id = data["patient_id"]
    
    date = data["date"]
    time = data["time"]
    
    # Prevent booking past dates
    today = datetime.today().date()
    appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
    
    if appointment_date < today:
        return jsonify({"message": "Cannot book appointment for past dates"}), 400

    # Check if doctor already has appointment at this time
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=date,
        time=time,
        status="booked"
    ).first()

    if existing:
        return jsonify({"message": "Doctor already booked for this time"}), 400

    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        date=date,
        time=time,
        status="booked"
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment booked successfully"})


# Cancel appointment
@patient.route("/patient/cancel_appointment", methods=["POST"])
def cancel_appointment():

    data = request.json
    appointment_id = data["appointment_id"]

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    if appointment.status != "booked":
        return jsonify({ "message": f"Cannot cancel appointment with status '{appointment.status}'"
    }), 400

    appointment.status = "cancelled"
    db.session.commit()

    return jsonify({"message": "Appointment cancelled"})


# Upcoming appointments
@patient.route("/patient/upcoming/<int:patient_id>", methods=["GET"])
def upcoming_appointments(patient_id):

    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    result = []

    for appt in appointments:
        doctor = Doctor.query.get(appt.doctor_id)
        
        result.append({ 
        "appointment_id": appt.id,
        "doctor": doctor.name if doctor else None,
        "date": appt.date,
        "time": appt.time,
        "status": appt.status
        })

    return jsonify(result)


# Patient history
@patient.route("/patient/history/<int:patient_id>", methods=["GET"])
def patient_history(patient_id):

    cache_key = f"patient_history_{patient_id}"

    cached_data = get_cache(cache_key)

    if cached_data:
        return jsonify(cached_data)

    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    history = []

    for appt in appointments:
        
        doctor = Doctor.query.get(appt.doctor_id)
        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()

        history.append({
            "appointment_id": appt.id,
            "doctor": doctor.name if doctor else None,
            "date": appt.date,
            "status": appt.status,
            "diagnosis": treatment.diagnosis if treatment else None,
            "prescription": treatment.prescription if treatment else None
        })
    
    set_cache(cache_key, history, expiry=60)

    return jsonify(history)


# Update profile
@patient.route("/patient/update_profile/<int:patient_id>", methods=["PUT"])
def update_profile(patient_id):

    data = request.json

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    patient.age = data.get("age", patient.age)
    patient.phone = data.get("phone", patient.phone)

    db.session.commit()

    return jsonify({"message": "Profile updated"})

from flask import send_file
import pandas as pd

@patient.route("/export-csv/<int:patient_id>")
def export_csv_route(patient_id):

    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    data = []

    for appt in appointments:

        doctor = Doctor.query.get(appt.doctor_id)
        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()

        data.append({
            "Doctor": doctor.name if doctor else None,
            "Date": appt.date,
            "Status": appt.status,
            "Diagnosis": treatment.diagnosis if treatment else None,
            "Prescription": treatment.prescription if treatment else None
        })

    df = pd.DataFrame(data)

    file_name = f"patient_{patient_id}_history.csv"

    df.to_csv(file_name, index=False)

    return send_file(file_name, as_attachment=True)

# -------------------------
# Get Departments
# -------------------------

@patient.route("/patient/departments", methods=["GET"])
def get_departments():

    departments = Department.query.all()

    result = []

    for d in departments:
        result.append({
            "id": d.id,
            "name": d.name
        })

    return jsonify(result)

# -------------------------
# Doctors by Department
# -------------------------

@patient.route("/patient/doctors/<int:department_id>", methods=["GET"])
def doctors_by_department(department_id):

    doctors = Doctor.query.filter_by(department_id=department_id).all()

    result = []

    for d in doctors:
        result.append({
            "doctor_id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "availability": d.availability
        })

    return jsonify(result)

# -------------------------
# Get Patient Profile
# -------------------------

@patient.route("/patient/profile/<int:patient_id>", methods=["GET"])
def get_profile(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    user = patient.user

    return jsonify({
        "name": patient.name,
        "email": user.email if user else None,
        "age": patient.age,
        "phone": patient.phone
    })