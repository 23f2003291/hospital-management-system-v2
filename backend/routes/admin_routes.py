from flask import Blueprint, jsonify, request
from models import db, User, Doctor, Patient, Appointment, Treatment
from werkzeug.security import generate_password_hash

admin = Blueprint("admin", __name__)


# -------------------------
# Admin Dashboard
# -------------------------

@admin.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():

    doctor_count = Doctor.query.count()
    patient_count = Patient.query.count()
    appointment_count = Appointment.query.count()

    return jsonify({
        "total_doctors": doctor_count,
        "total_patients": patient_count,
        "total_appointments": appointment_count
    })


# -------------------------
# Add Doctor
# -------------------------

@admin.route("/admin/add_doctor", methods=["POST"])
def add_doctor():

    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    department_id = data.get("department_id")
    specialization = data.get("specialization")

    if not username or not email or not password or not specialization:
        return jsonify({"message": "Missing required fields"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role="doctor"
    )

    db.session.add(new_user)
    db.session.commit()

    doctor = Doctor(
        user_id=new_user.id,
        name=username,
        specialization=specialization,
        department_id=department_id,
        availability="Not set"
    )

    db.session.add(doctor)
    db.session.commit()

    return jsonify({
        "message": "Doctor added successfully",
        "doctor_id": doctor.id
    })


# -------------------------
# Update Doctor Profile
# -------------------------

@admin.route("/admin/update_doctor/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404

    data = request.json

    doctor.name = data.get("name", doctor.name)
    doctor.specialization = data.get("specialization", doctor.specialization)
    doctor.availability = data.get("availability", doctor.availability)

    db.session.commit()

    return jsonify({"message": "Doctor updated successfully"})


# -------------------------
# Search Doctors
# -------------------------

@admin.route("/admin/search_doctors", methods=["GET"])
def search_doctors():

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
            "id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "department": d.department.name if d.department else None,
            "availability": d.availability
        })

    return jsonify(result)


# -------------------------
# Search Patients
# -------------------------

@admin.route("/admin/search_patients", methods=["GET"])
def search_patients():

    name = request.args.get("name")
    phone = request.args.get("phone")

    query = Patient.query

    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))

    if phone:
        query = query.filter(Patient.phone.ilike(f"%{phone}%"))

    patients = query.all()

    result = []

    for p in patients:
        result.append({
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "phone": p.phone
        })

    return jsonify(result)


# -------------------------
# View All Appointments
# -------------------------

@admin.route("/admin/appointments", methods=["GET"])
def view_appointments():

    appointments = Appointment.query.all()

    result = []

    for a in appointments:

        doctor = Doctor.query.get(a.doctor_id)
        patient = Patient.query.get(a.patient_id)

        result.append({
            "appointment_id": a.id,
            "doctor_name": doctor.name if doctor else None,
            "patient_id": a.patient_id,
            "patient_name": patient.name if patient else None,
            "date": a.date,
            "time": a.time,
            "status": a.status
        })

    return jsonify(result)
# -------------------------
# View Patient Treatment History 
# -------------------------

@admin.route("/admin/patient_history/<int:patient_id>", methods=["GET"])
def admin_patient_history(patient_id):

    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    history = []

    for appt in appointments:

        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()
        doctor = Doctor.query.get(appt.doctor_id)

        history.append({
            "appointment_id": appt.id,
            "doctor_id": appt.doctor_id,
            "doctor_name": doctor.name if doctor else None,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status,
            "diagnosis": treatment.diagnosis if treatment else None,
            "prescription": treatment.prescription if treatment else None,
            "notes": treatment.notes if treatment else None
        })

    return jsonify(history)


# -------------------------
# Remove / Blacklist Doctor
# -------------------------

@admin.route("/admin/remove_doctor/<int:doctor_id>", methods=["DELETE"])
def remove_doctor(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404

    user = User.query.get(doctor.user_id)

    db.session.delete(doctor)

    if user:
        db.session.delete(user)

    db.session.commit()

    return jsonify({"message": "Doctor removed successfully"})


# -------------------------
# Remove / Blacklist Patient
# -------------------------

@admin.route("/admin/remove_patient/<int:patient_id>", methods=["DELETE"])
def remove_patient(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    user = User.query.get(patient.user_id)

    db.session.delete(patient)

    if user:
        db.session.delete(user)

    db.session.commit()

    return jsonify({"message": "Patient removed successfully"})