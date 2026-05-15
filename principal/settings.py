import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(env_path):
    values = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


ENV_VALUES = _load_env_file(BASE_DIR / ".env")


def env(name, default=""):
    return os.getenv(name, ENV_VALUES.get(name, default))

SECRET_KEY = "django-insecure-(6)9+nt=!u!frx$+3fm#jlrng63z=&9w9xc6==8eaq2)vx83r2"

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.parametro.apps.ParametroConfig",
    "apps.usuario.apps.UsuarioConfig",
    "apps.datos_personales.apps.DatosPersonalesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "principal.urls"

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
                "principal.context_processors.panel_context",
            ],
        },
    },
]

WSGI_APPLICATION = "principal.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


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


LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    "principal.auth_backends.ActiveProfileModelBackend",
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "usuario:psicologo_list"
LOGOUT_REDIRECT_URL = "home"


CORREO_OFICIAL = env("CORREO_OFICIAL", "no-reply@menteclara.local")
PASSWORD_CORREO = env("PASSWORD_CORREO", "")


def _infer_email_host(address):
    domain = address.split("@", 1)[1].lower() if "@" in address else ""
    if domain in {"gmail.com", "googlemail.com"}:
        return "smtp.gmail.com"
    if domain in {"outlook.com", "hotmail.com", "live.com", "office365.com"}:
        return "smtp.office365.com"
    if domain:
        return f"smtp.{domain}"
    return "localhost"


EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend" if PASSWORD_CORREO else "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", _infer_email_host(CORREO_OFICIAL))
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", CORREO_OFICIAL)
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", PASSWORD_CORREO)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
EMAIL_USE_SSL = env("EMAIL_USE_SSL", "false").lower() in {"1", "true", "yes", "on"}
DEFAULT_FROM_EMAIL = CORREO_OFICIAL
SERVER_EMAIL = CORREO_OFICIAL
