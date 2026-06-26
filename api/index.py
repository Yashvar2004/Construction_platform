import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_platfrom.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Expose WSGI app for Vercel
app = get_wsgi_application()
