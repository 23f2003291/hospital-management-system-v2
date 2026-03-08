from flask import Blueprint, request, jsonify
from models import db, User, Patient, Doctor
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


# ---------------------------
# Patient Registration
# ---------------------------
# Only patients can register themselves
# Doctors are added by Admin
# Admin is pre-created programmatically
# ---------------------------

@auth.route("/register", methods=["POST"])
def register():

    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    age = data.get("age", 0)
    phone = data.get("phone", "Not provided")


    # Validate input
    if not username or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    # Hash password before storing
    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role="patient"
    )

    db.session.add(new_user)
    db.session.commit()

    # Create patient profile
    patient = Patient(
        user_id=new_user.id,
        name=username,
        age=age,
        phone=phone
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient registered successfully"
    })


# ---------------------------
# Login (Admin / Doctor / Patient)
# ---------------------------

@auth.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    # Find user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    # Verify hashed password
    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Role-based redirect
     
    if user.role == "admin":
        return jsonify({
        "message": "Login successful",
        "role": user.role,
        "user_id": user.id,
        "redirect": "/admin/dashboard"
    })
    
    elif user.role == "doctor":
        
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        
        return jsonify({
        "message": "Login successful",
        "role": user.role,
        "user_id": user.id,
        "doctor_id": doctor.id if doctor else None,
        "redirect": "/doctor/dashboard"
    })
    
    else:  # patient
        
        patient = Patient.query.filter_by(user_id=user.id).first()
        
        return jsonify({
        "message": "Login successful",
        "role": user.role,
        "user_id": user.id,
        "patient_id": patient.id if patient else None,
        "redirect": "/patient/dashboard"
    })


# ---------------------------
# Logout (simple endpoint)
# ---------------------------

@auth.route("/logout", methods=["POST"])
def logout():
    return jsonify({
        "message": "Logged out successfully"
    })