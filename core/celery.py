import os
from celery import Celery

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Create Celery app
app = Celery("core")

# Load settings with CELERY_ namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Update configuration
app.conf.update(
    result_backend="django-db",
    beat_scheduler="django_celery_beat.schedulers:DatabaseScheduler",  # Use django-celery-beat
)

# Autodiscover tasks
app.autodiscover_tasks()


# Debug task
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
