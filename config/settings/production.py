"""Production settings — used by Gunicorn behind Nginx in Docker."""

from .base import *  # noqa: F403

DEBUG = env_bool("DEBUG", False)  # noqa: F405

# Required. The container refuses to start without it (see docker/entrypoint.sh).
SECRET_KEY = os.environ["SECRET_KEY"]  # noqa: F405

# e.g. ALLOWED_HOSTS=example.com,www.example.com,.example.com
# A leading dot ("​.example.com") also matches every project subdomain.
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])  # noqa: F405

# e.g. CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", [])  # noqa: F405


# --- Security -----------------------------------------------------------------
# Nginx terminates TLS and forwards the original scheme in X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Turn the HTTPS-only flags off (SECURE_SSL_ENABLED=0) while you are still
# serving plain HTTP, e.g. before certificates are issued.
_https = env_bool("SECURE_SSL_ENABLED", True)  # noqa: F405

SECURE_SSL_REDIRECT = _https
SESSION_COOKIE_SECURE = _https
CSRF_COOKIE_SECURE = _https
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000")) if _https else 0  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)  # noqa: F405
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)  # noqa: F405

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "SAMEORIGIN"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # the theme toggle reads no cookies, but forms post

# Nginx already handles static/media; WhiteNoise is kept as a safety net so the
# app also works when run without a reverse proxy.
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365


# --- Caching ------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "portfolio-default",
    }
}

if os.environ.get("REDIS_URL"):  # noqa: F405
    CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ["REDIS_URL"],  # noqa: F405
    }

# Cache rendered image renditions lookups — cheap win for image-heavy pages.
WAGTAILIMAGES_CACHE_RENDITIONS = True


# --- Error reporting ----------------------------------------------------------
ADMINS = [
    ("Site owner", email)
    for email in env_list("ADMIN_EMAILS", [])  # noqa: F405
]
MANAGERS = ADMINS

LOGGING["loggers"]["django.request"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "ERROR",
    "propagate": False,
}

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
