from celery import Celery
from celery.schedules import crontab

celery = Celery(
    "hospital",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

import tasks

# Scheduled jobs
celery.conf.beat_schedule = {
    
    "daily-reminder-job": {
        "task": "tasks.daily_reminder",
        "schedule": crontab(hour=8, minute=0),  # every day at 8 AM
    },

    "monthly-doctor-report": {
        "task": "tasks.monthly_doctor_report",
        "schedule": crontab(day_of_month=1, hour=9, minute=0),
    }
}