from pathlib import Path
from secrets import token_urlsafe

BASE_DIR = Path(__file__).resolve().parent.parent
# Local demo settings. No accounts or persistent records yet.
SECRET_KEY = token_urlsafe(50)
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver"]
ROOT_URLCONF = "fasal.urls"
INSTALLED_APPS = ["django.contrib.staticfiles", "fasal"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
TEMPLATES = [
    {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
]
STATIC_URL = "/static/"
LANGUAGE_CODE = "en"
TIME_ZONE = "Asia/Karachi"
USE_TZ = True
