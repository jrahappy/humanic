from pathlib import Path
import os
import sys
import djcelery
import redis

# This is for celery
djcelery.setup_loader()

# Celery settings
CELERY_BROKER_URL = "redis://clustercfg.humanradsuda.9qxagu.memorydb.us-east-2.amazonaws.com:6379/0"  # Ensure this is correct
CELERY_RESULT_BACKEND = "django-db"  # Using Django database as the result backend

# Optional: Set a timeout for Redis connections
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
