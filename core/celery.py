import os
from celery import Celery

# Set the correct Django settings module for the 'celery' program.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "core.settings"
)  # Ensure 'core.settings' is correct.

app = Celery("core")

# Load Celery configuration from Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Celery's result backend using Django's database.
app.conf.update(
    result_backend="django-db",
)

# Autodiscover tasks from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
