import environ
import os
from pathlib import Path

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
# DEBUG = True

ALLOWED_HOSTS = [
    "humanrad.com",
    "www.humanrad.com",
    "127.0.0.1",
    "44.220.242.249",
    "172.26.9.185",
]

SITE_ID = 1


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_extensions",
    "django_filters",
    "django_celery_results",
    "widget_tweaks",
    "allauth",
    "allauth.account",
    "django_htmx",
    "tailwind",
    "theme",
    "django_browser_reload",
    "crispy_forms",
    "crispy_tailwind",
    "import_export",
    "celery_progress",
    "django_recaptcha",
    "ckeditor",
    "taggit",
    "django_cleanup.apps.CleanupConfig",
    # "ckeditor_uploader",
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
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

# Debug toolbar settings
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

DEBUG_TOOLBAR_CONFIG = {
    # "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG  # Show toolbar only in DEBUG mode
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

# LOGOUT_REDIRECT_URL = "web:index"
# ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True

# ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = "none"
# ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_FORMS = {
    "signup": "accounts.forms.CustomUserCreationForm",
}


AUTH_USER_MODEL = "accounts.CustomUser"

ROOT_URLCONF = "core.urls"

TAILWIND_APP_NAME = "theme"
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
INTERNAL_IPS = [
    "127.0.0.1",
]
TAILWIND_CSS_PATH = "css/dist/styles.css"
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
        "CONN_MAX_AGE": 60,  # Set the connection age to 1 hour
        # "OPTIONS": {
        #     "connect_timeout": 3660,  # Increase the connection timeout to 30 seconds
        # },
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

# LANGUAGE_CODE = "en-us"
LANGUAGE_CODE = "ko-kr"

# TIME_ZONE = "UTC"
TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "/static/"  # URL for accessing static files
STATIC_ROOT = (
    BASE_DIR / "static/"
)  # Folder where 'collectstatic' will store static files

# Media files (user-uploaded content)
MEDIA_URL = "/media/"  # URL for accessing media files
MEDIA_ROOT = BASE_DIR / "media/"  # Folder where uploaded media files will be stored

STATICFILES_DIRS = [BASE_DIR / "theme" / "static"]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# AWS_QUERYSTRING_AUTH = False
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")

CKEDITOR_CONFIGS = {
    "default": {
        "height": 800,
        "width": 1200,
        "removePlugins": "exportpdf",
    }
}

TAGGIT_CASE_INSENSITIVE = True
