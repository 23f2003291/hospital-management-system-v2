from flask import Flask
from config import Config
from models import db, User, Department
from werkzeug.security import generate_password_hash
from flask_cors import CORS

from routes.auth_routes import auth
from routes.dashboard_routes import dashboard
from routes.admin_routes import admin
from routes.doctor_routes import doctor
from routes.patient_routes import patient

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(dashboard)
app.register_blueprint(doctor)
app.register_blueprint(patient)

CORS(app)

db.init_app(app)

@app.route("/")
def home():
    return "Hospital Management System Running"


with app.app_context():

    db.create_all()

    # Create admin automatically
    admin = User.query.filter_by(role="admin").first()

    if not admin:
        admin = User(
            username="admin",
            email="admin@hospital.com",
            password=generate_password_hash("admin123"),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully")
    
    # -------------------------
    # Create default departments
    # -------------------------
    if Department.query.count() == 0:

        departments = [

            Department(name="Cardiology", description="Heart related treatments"),
            Department(name="Oncology", description="Cancer treatment"),
            Department(name="General", description="General consultation")

        ]

        db.session.add_all(departments)
        db.session.commit()

        print("Departments created")

if __name__ == "__main__":
    app.run(debug=True)