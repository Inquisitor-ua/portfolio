"""Development settings — never use these in production."""

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = os.environ.get(  # noqa: F405
    "SECRET_KEY", "django-insecure-dev-only-key-change-me-in-production"
)

ALLOWED_HOSTS = ["*"]

# Allow the dev server to be reached over any localhost-ish host/subdomain.
CSRF_TRUSTED_ORIGINS = env_list(  # noqa: F405
    "CSRF_TRUSTED_ORIGINS",
    ["http://localhost:8000", "http://127.0.0.1:8000"],
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Serve static files straight from disk — no manifest, no collectstatic needed.
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

# Show the Wagtail styleguide and make debugging templates easier.
INTERNAL_IPS = ["127.0.0.1", "::1"]

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
