from flask import Flask
from config import Config
from models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

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


if __name__ == "__main__":
    app.run(debug=True)