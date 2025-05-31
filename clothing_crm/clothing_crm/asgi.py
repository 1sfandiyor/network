"""
ASGI config for clothing_crm project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clothing_crm.settings')

application = get_asgi_application()