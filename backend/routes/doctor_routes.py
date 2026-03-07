from flask import Blueprint, jsonify, request
from models import db, Appointment, Treatment, Doctor, Patient

doctor = Blueprint("doctor", __name__)


# -------------------------
# Doctor Dashboard - View Appointments
# -------------------------

@doctor.route("/doctor/appointments/<int:doctor_id>", methods=["GET"])
def doctor_appointments(doctor_id):

    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()

    result = []

    for appt in appointments:
        result.append({
            "appointment_id": appt.id,
            "patient_id": appt.patient_id,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status
        })

    return jsonify(result)


# -------------------------
# View Assigned Patients
# -------------------------

@doctor.route("/doctor/patients/<int:doctor_id>", methods=["GET"])
def doctor_patients(doctor_id):

    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()

    patient_ids = set()

    for appt in appointments:
        patient_ids.add(appt.patient_id)

    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()

    result = []

    for p in patients:
        result.append({
            "patient_id": p.id,
            "name": p.name,
            "age": p.age,
            "phone": p.phone
        })

    return jsonify(result)


# -------------------------
# Complete Appointment + Add Treatment
# -------------------------

@doctor.route("/doctor/complete", methods=["POST"])
def complete_appointment():

    data = request.json

    appointment_id = data["appointment_id"]
    diagnosis = data["diagnosis"]
    prescription = data["prescription"]
    notes = data["notes"]

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    # Only booked appointments can be completed
    if appointment.status != "booked":
        return jsonify({
            "message": f"Cannot complete appointment with status '{appointment.status}'"
        }), 400

    appointment.status = "completed"

    treatment = Treatment(
        appointment_id=appointment_id,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=notes
    )

    db.session.add(treatment)
    db.session.commit()

    return jsonify({"message": "Appointment completed and treatment added"})


# -------------------------
# Cancel Appointment
# -------------------------

@doctor.route("/doctor/cancel_appointment", methods=["POST"])
def cancel_appointment():

    data = request.json
    appointment_id = data["appointment_id"]

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    # Only booked appointments can be cancelled
    if appointment.status != "booked":
        return jsonify({
            "message": f"Cannot cancel appointment with status '{appointment.status}'"
        }), 400

    appointment.status = "cancelled"
    db.session.commit()

    return jsonify({"message": "Appointment cancelled"})


# -------------------------
# Update Doctor Availability
# -------------------------

@doctor.route("/doctor/update_availability/<int:doctor_id>", methods=["PUT"])
def update_availability(doctor_id):

    data = request.json
    availability = data["availability"]

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404

    doctor.availability = availability
    db.session.commit()

    return jsonify({"message": "Availability updated"})


# -------------------------
# View Patient Medical History
# -------------------------

@doctor.route("/doctor/patient_history/<int:patient_id>", methods=["GET"])
def patient_history(patient_id):

    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    history = []

    for appt in appointments:

        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()

        history.append({
            "appointment_id": appt.id,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status,
            "diagnosis": treatment.diagnosis if treatment else None,
            "prescription": treatment.prescription if treatment else None,
            "notes": treatment.notes if treatment else None
        })

    return jsonify(history)