from flask import Blueprint, jsonify
from models import db, Appointment, Doctor, Patient

dashboard = Blueprint('dashboard', __name__)

@dashboard.route("/doctor/dashboard/<int:doctor_id>", methods=["GET"])
def doctor_dashboard(doctor_id):

    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()

    total = len(appointments)
    completed = 0
    pending = 0

    upcoming = []

    for appt in appointments:

        if appt.status == "completed":
            completed += 1
        else:
            pending += 1

        upcoming.append({
            "appointment_id": appt.id,
            "patient_id": appt.patient_id,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status
        })

    return jsonify({
        "total_appointments": total,
        "completed": completed,
        "pending": pending,
        "appointments": upcoming
    })

@dashboard.route("/patient/dashboard")
def patient_dashboard():
    return jsonify({"message": "Patient Dashboard"})