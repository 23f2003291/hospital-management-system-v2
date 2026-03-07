from flask import Blueprint, jsonify, request
from models import db, Doctor, Patient, Appointment, Treatment

patient = Blueprint("patient", __name__)


# View doctors / search
@patient.route("/patient/doctors", methods=["GET"])
def view_doctors():

    name = request.args.get("name")
    specialization = request.args.get("specialization")

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

    return jsonify(result)


# Book appointment
@patient.route("/patient/book_appointment", methods=["POST"])
def book_appointment():

    data = request.json

    doctor_id = data["doctor_id"]
    patient_id = data["patient_id"]
    date = data["date"]
    time = data["time"]

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
        result.append({
            "appointment_id": appt.id,
            "doctor_id": appt.doctor_id,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status
        })

    return jsonify(result)


# Patient history
@patient.route("/patient/history/<int:patient_id>", methods=["GET"])
def patient_history(patient_id):

    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    history = []

    for appt in appointments:

        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()

        history.append({
            "appointment_id": appt.id,
            "date": appt.date,
            "status": appt.status,
            "diagnosis": treatment.diagnosis if treatment else None,
            "prescription": treatment.prescription if treatment else None
        })

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