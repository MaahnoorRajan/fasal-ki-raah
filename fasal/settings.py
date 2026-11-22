from pathlib import Path
from secrets import token_urlsafe
import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
# Local prototype. Set a stable secret to retain sessions across restarts.
DEBUG = os.environ.get("FASAL_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("FASAL_SECRET_KEY") or (token_urlsafe(50) if DEBUG else "")
ALLOWED_HOSTS = [host.strip() for host in os.environ.get(
    "FASAL_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1],testserver" if DEBUG else "",
).split(",") if host.strip()]
if not DEBUG and (not SECRET_KEY or not ALLOWED_HOSTS):
    raise ImproperlyConfigured("Set FASAL_SECRET_KEY and FASAL_ALLOWED_HOSTS for deployment.")
ROOT_URLCONF = "fasal.urls"
INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.staticfiles", "fasal"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
TEMPLATES = [
    {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
]
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
WSGI_APPLICATION = "fasal.wsgi.application"
LANGUAGE_CODE = "en"
TIME_ZONE = "Asia/Karachi"
USE_TZ = True
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.environ.get("FASAL_DATABASE_PATH", str(BASE_DIR / "db.sqlite3")),
    "OPTIONS": {"timeout": 20},
}}
if not DEBUG and not os.environ.get("FASAL_DATABASE_PATH"):
    raise ImproperlyConfigured("Set FASAL_DATABASE_PATH to a database on persistent storage.")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
SECURE_HSTS_SECONDS = 3600 if not DEBUG else 0
SECURE_CONTENT_TYPE_NOSNIFF = True
# Enable only behind a proxy that strips client-supplied forwarded headers.
if os.environ.get("FASAL_TRUST_PROXY") == "1":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get("FASAL_CSRF_ORIGINS", "").split(",") if origin.strip()
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "driver-login"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
