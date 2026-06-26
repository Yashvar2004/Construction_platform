import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mark as running on Vercel
os.environ['VERCEL'] = '1'

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_platfrom.settings')

# Initialize Django
import django
django.setup()

# Run migrations on cold start (Vercel /tmp is ephemeral)
from django.core.management import call_command
try:
    call_command('migrate', '--run-syncdb', verbosity=0)
except Exception:
    pass  # Migrations may already be applied

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Expose WSGI app for Vercel
app = get_wsgi_application()
