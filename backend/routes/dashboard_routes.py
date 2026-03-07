from flask import Blueprint, jsonify
from models import db, Appointment, Doctor, Patient

dashboard = Blueprint('dashboard', __name__)


@dashboard.route("/doctor/dashboard")
def doctor_dashboard():
    return jsonify({"message": "Doctor Dashboard"})

@dashboard.route("/patient/dashboard")
def patient_dashboard():
    return jsonify({"message": "Patient Dashboard"})