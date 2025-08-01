import environ
import os
from pathlib import Path

env = environ.Env(DEBUG=(bool, False))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_extensions",
    "django_vite",
    "rest_framework",
    "storages",
    "django_filters",
    "django_celery_results",
    "django_celery_beat",
    "widget_tweaks",
    "allauth",
    "allauth.account",
    "django_htmx",
    "import_export",
    "celery_progress",
    "django_recaptcha",
    "django_summernote",
    "taggit",
    "django_cleanup.apps.CleanupConfig",
    "dogfoot",
    "utils",
    "minibooks",
    "accounts",
    "customer",
    "provider",
    "product",
    "importdata",
    "briefing",
    "report",
    "blog",
    "referdex",
    "crm",
    "collab",
    "task",
    "web",
    "api",
    "chat",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

# Debug toolbar settings
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG  # Show toolbar only in DEBUG mode
}

# Authentication settings
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGIN_REDIRECT_URL = "blog:index"
ACCOUNT_LOGOUT_REDIRECT = "web:index"

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_FORMS = {
    "signup": "accounts.forms.CustomUserCreationForm",
}

AUTH_USER_MODEL = "accounts.CustomUser"

ROOT_URLCONF = "core.urls"

INTERNAL_IPS = [
    "127.0.0.1",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": env("REDIS_URL"),
                    "password": env("REDIS_PASSWORD"),
                }
            ],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_NAME"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
        "CONN_MAX_AGE": 300,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# Storage settings for static and media files
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN")

# Media files (user-uploaded content)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "assets",
    BASE_DIR / "static",
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

if DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",  # Keep S3 for media files if desired
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",  # For local static files in development
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",  # Keep S3 for media files if desired
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",  # For static files (or keep ManifestStaticFilesStorage)
            "OPTIONS": {
                "location": "static",  # Optional: specify a location for static files in S3
            },
        },
    }


DJANGO_VITE = {
    "default": {
        "dev_mode": env("DEBUG"),
    }
}

# Adjust file upload size
DATA_UPLOAD_MAX_NUMBER_FILES = 600
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")

TAGGIT_CASE_INSENSITIVE = True

# Summernote settings
SUMMERNOTE_CONFIG = {
    "iframe": True,
    "summernote": {
        "width": "100%",
        "height": "480",
        "toolbar": [
            ["style", ["style"]],
            ["font", ["bold", "underline", "clear"]],
            ["fontname", ["fontname"]],
            ["color", ["color"]],
            ["para", ["ul", "ol", "paragraph"]],
            ["table", ["table"]],
            ["insert", ["link", "picture", "video"]],
            ["view", ["fullscreen", "codeview", "help"]],
        ],
    },
    "attachment_filesize_limit": 4 * 1024 * 1024,  # 4MB
    "attachment_require_authentication": True,
    "css": (
        "//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/theme/monokai.min.css",
    ),
    "codemirror": {
        "mode": "htmlmixed",
        "lineNumbers": "true",
        "theme": "monokai",
    },
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# CELERY_RESULT_BACKEND = env(
#     "CELERY_RESULT_BACKEND"
# )  # Use Django database for storing task results
CELERY_RESULT_BACKEND = "django-db"  # Use Django database for storing task results
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"  # Use django-celery-beat for periodic tasks
CELERY_RESULT_EXTENDED = True  # Store extended result information

CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": 3600,  # 1 hour
}
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Seoul"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
