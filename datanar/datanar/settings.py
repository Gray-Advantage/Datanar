from pathlib import Path
import sys

from decouple import config
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

VERSION = "2.6.6"
API_VERSION = "1.2.1"

SECRET_KEY = config(
    "DATANAR_SECRET_KEY",
    default="this_is_test_key_-_some_very_dummy_secret_key",
    cast=str,
)

DEBUG = config("DATANAR_DJANGO_DEBUG", False, cast=bool)
TEST = "test" in sys.argv

LOG_FILE_PATH = config("DATANAR_LOG_FILE_PATH", default="", cast=str)

if LOG_FILE_PATH:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "\n{levelname}\n{asctime}\n>>> {message}",
                "style": "{",
            },
        },
        "handlers": {
            "file": {
                "level": "WARNING",
                "class": "logging.FileHandler",
                "filename": LOG_FILE_PATH,
                "formatter": "verbose",
            },
        },
        "root": {
            "handlers": ["file"],
            "level": "WARNING",
        },
    }

ALLOWED_HOSTS = config(
    "DATANAR_ALLOWED_HOSTS",
    default="*",
    cast=lambda line: line.split(","),
)

CSRF_TRUSTED_ORIGINS = [f"https://{x}" for x in ALLOWED_HOSTS]
CSRF_FAILURE_VIEW = "core.views.csrf_failure"

TRUSTED_PROXIES = config(
    "DATANAR_TRUSTED_PROXIES",
    default="172.16.0.0/12,127.0.0.1/32",
    cast=lambda line: [x for x in line.split(",") if x],
)
REAL_IP_HEADER = config(
    "DATANAR_REAL_IP_HEADER",
    default="HTTP_X_REAL_IP",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_cleanup",
    "sorl.thumbnail",
    "django_user_agents",
    "rest_framework",
    "rest_framework.authtoken",
    "api.apps.ApiConfig",
    "dashboard.apps.DashboardConfig",
    "core.apps.CoreConfig",
    "qr_codes.apps.QrCodesConfig",
    "homepage.apps.HomepageConfig",
    "users.apps.UsersConfig",
    "redirects.apps.RedirectsConfig",
    "statistic.apps.StatisticConfig",
    "allauth",
    "allauth.account",
    "tz_detect",
]

MIDDLEWARE = [
    "core.middleware.RealIPMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "tz_detect.middleware.TimezoneMiddleware",
]

if DEBUG and not TEST:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "datanar.urls"

TEMPLATES_DIR = BASE_DIR / "templates"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATES_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_settings_export.settings_export",
                "core.context_processors.server_url",
            ],
        },
    },
]

WSGI_APPLICATION = "datanar.wsgi.application"

USE_FILE_DATABASE = config(
    "DATANAR_USE_FILE_DATABASE",
    default=True,
    cast=bool,
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": (
            BASE_DIR
            / f"{config('DATANAR_DATABASE_NAME', default='db')}.sqlite3"
        ),
    },
}

if not USE_FILE_DATABASE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DATANAR_DATABASE_NAME"),
            "USER": config("DATANAR_DATABASE_USER"),
            "PASSWORD": config("DATANAR_DATABASE_PASSWORD"),
            "HOST": config("DATANAR_DATABASE_HOST"),
            "PORT": config("DATANAR_DATABASE_PORT"),
        },
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation"
            ".UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "users.User"

DEFAULT_USER_IS_ACTIVE = config(
    "DATANAR_DEFAULT_USER_IS_ACTIVE",
    default=False,
    cast=bool,
)

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_CHANGE_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_VERIFICATION = "none" if DEFAULT_USER_IS_ACTIVE else "mandatory"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
UNCONFIRMED_USER_TTL_DAYS = config(
    "DATANAR_UNCONFIRMED_USER_TTL_DAYS",
    default=ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS,
    cast=int,
)

SITE_ID = config("DATANAR_SITE_ID", default=1, cast=int)
SITE_NAME = config("DATANAR_SITE_NAME", default="Datanar", cast=str)

EMAIL_HOST = config("DATANAR_MAIL_HOST", default="smtp.mail.ru")
EMAIL_PORT = config("DATANAR_MAIL_PORT", default=2525, cast=int)
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = (
    f"{SITE_NAME} "
    f"<{config('DATANAR_MAIL_USER', default='webmaster@localhost')}>"
)
EMAIL_HOST_USER = config("DATANAR_MAIL_USER", default="webmaster@localhost")
EMAIL_HOST_PASSWORD = config(
    "DATANAR_MAIL_PASSWORD",
    default="this_very_secret_password_for_smtp_mail",
)

LANGUAGE_CODE = "ru-ru"

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
    ("uk", _("Ukrainian")),
    ("bg", _("Bulgarian")),
    ("de", _("German")),
    ("es", _("Spanish")),
    ("fr", _("French")),
    ("ja", _("Japanese")),
]

LOCALE_PATHS = (BASE_DIR / "locale/",)

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static_dev/",
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

GEOIP_PATH = "geo_ip"

CELERY_BROKER_URL = (
    f"redis://{config('DATANAR_REDIS_HOST', default='localhost', cast=str)}:"
    f"{config('DATANAR_REDIS_PORT', default='6379', cast=str)}/"
    f"{config('DATANAR_REDIS_DB', default='0', cast=str)}"
)
CELERY_RESULT_BACKEND = (
    f"redis://{config('DATANAR_REDIS_HOST', default='localhost', cast=str)}:"
    f"{config('DATANAR_REDIS_PORT', default='6379', cast=str)}/"
    f"{config('DATANAR_REDIS_DB', default='0', cast=str)}"
)

SETTINGS_EXPORT = ["VERSION", "API_VERSION"]
