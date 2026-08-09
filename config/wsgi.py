"""
WSGI config — this is what Gunicorn imports.

The settings module defaults to production; the dev server overrides it via
manage.py, and Docker sets DJANGO_SETTINGS_MODULE explicitly.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
