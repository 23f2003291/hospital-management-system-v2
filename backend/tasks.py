from celery_worker import celery
import csv

from app import app
from models import db, Appointment


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


@celery.task
def daily_reminder():

    with app.app_context():

        print("Checking today's appointments")

        appointments = Appointment.query.filter_by(status="booked").all()

        for appt in appointments:

            print(f"Reminder: Patient {appt.patient_id} visit today")


@celery.task
def monthly_doctor_report():

    with app.app_context():

        print("Generating doctor monthly report")

        appointments = Appointment.query.all()

        for appt in appointments:

            print(f"Doctor {appt.doctor_id} handled appointment {appt.id}")