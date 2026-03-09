from celery_worker import celery
from datetime import date
import csv
import smtplib
from email.mime.text import MIMEText

from app import app
from models import db, Appointment, Doctor, Patient


# -------------------------
# EMAIL FUNCTION (MAILHOG)
# -------------------------

def send_email(to_email, subject, message):

    msg = MIMEText(message)

    msg["Subject"] = subject
    msg["From"] = "hospital@test.com"
    msg["To"] = to_email

    # MailHog SMTP
    server = smtplib.SMTP("localhost", 1025)

    server.sendmail("hospital@test.com", [to_email], msg.as_string())

    server.quit()



# -------------------------
# EXPORT CSV (ASYNC JOB)
# -------------------------

@celery.task
def export_csv():

    print("Exporting hospital data to CSV")

    with app.app_context():

        appointments = Appointment.query.all()

        with open("appointments_export.csv", "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Appointment ID",
                "Doctor",
                "Patient",
                "Date",
                "Status"
            ])

            for appt in appointments:

                writer.writerow([
                    appt.id,
                    appt.doctor_id,
                    appt.patient_id,
                    appt.date,
                    appt.status
                ])

    print("CSV Export Complete")



# -------------------------
# DAILY REMINDER
# -------------------------

@celery.task
def daily_reminder():

    with app.app_context():

        print("Checking today's appointments")

        today = date.today().isoformat()

        appointments = Appointment.query.filter_by(
            date=today,
            status="booked"
        ).all()

        for appt in appointments:

            patient = Patient.query.get(appt.patient_id)
            doctor = Doctor.query.get(appt.doctor_id)

            if patient and patient.user:

                email = patient.user.email

                message = f"""
Hospital Appointment Reminder

Dear Patient,

You have an appointment today.

Doctor: {doctor.name}
Date: {appt.date}
Time: {appt.time}

Please visit the hospital on time.

Regards,
Hospital Management System
"""

                send_email(
                    email,
                    "Hospital Appointment Reminder",
                    message
                )

        print("Daily reminders sent")



# -------------------------
# MONTHLY DOCTOR REPORT
# -------------------------

@celery.task
def monthly_doctor_report():

    with app.app_context():

        print("Generating doctor monthly reports")

        doctors = Doctor.query.all()

        for doctor in doctors:

            appointments = Appointment.query.filter_by(
                doctor_id=doctor.id
            ).all()

            report = f"Monthly Report for {doctor.name}\n\n"

            for appt in appointments:

                report += f"""
Appointment ID: {appt.id}
Patient ID: {appt.patient_id}
Date: {appt.date}
Status: {appt.status}

"""

            if doctor.user:

                email = doctor.user.email

                send_email(
                    email,
                    "Monthly Hospital Activity Report",
                    report
                )

        print("Monthly reports sent")