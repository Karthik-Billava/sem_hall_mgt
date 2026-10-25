"""
WSGI config for sem_hall_mgt project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sem_hall_mgt.settings')

application = get_wsgi_application()

# Wasmer's Django runtime looks for a WSGI callable named `app`.
app = application
