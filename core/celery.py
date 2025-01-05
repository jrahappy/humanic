import os
from celery import Celery

# Django 설정 모듈을 Celery가 사용하도록 등록
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")

app = Celery("your_project")

# Django 설정으로부터 Celery 구성 로드
app.config_from_object("django.conf:settings", namespace="CELERY")

# Django의 모든 등록된 앱에서 task 모듈 로드
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
