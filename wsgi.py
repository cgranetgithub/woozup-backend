import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
#site.addsitedir('~/.virtualenvs/myprojectenv/local/lib/python2.7/site-packages')
site.addsitedir('/home/geoevent/venv/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/geoevent/geoevent/')
#sys.path.append('/home/django_projects/MyProject/myproject')

os.environ['DJANGO_SETTINGS_MODULE'] = 'service.settings.vm'
os.environ['GEOS_LIBRARY_PATH'] = '/usr/lib/libgeos_c.so.1'
os.environ['GDAL_LIBRARY_PATH'] = '/usr/lib/libgdal.so.1'
os.environ['PROJ4_LIBRARY_PATH'] = '/usr/lib/libproj.so'

os.environ['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID', '')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
os.environ['AWS_STORAGE_BUCKET_NAME'] = 'geoevent-static'

os.environ['GCM_API_KEY'] = os.environ.get('GCM_API_KEY', '')

os.environ['PAPERTRAIL_API_TOKEN'] = os.environ.get('PAPERTRAIL_API_TOKEN', '')

os.environ['PLIVO_AUTH_ID'] = os.environ.get('PLIVO_AUTH_ID', '')
os.environ['PLIVO_AUTH_TOKEN'] = os.environ.get('PLIVO_AUTH_TOKEN', '')
os.environ['PLIVO_SENDER_PHONE'] = os.environ.get('PLIVO_SENDER_PHONE', '')

os.environ['SENDGRID_PASSWORD'] = os.environ.get('SENDGRID_PASSWORD', '')
os.environ['SENDGRID_USERNAME'] = os.environ.get('SENDGRID_USERNAME', '')


os.environ['SECRET_KEY'] = os.environ.get('SECRET_KEY', '')
os.environ['PYTHONHASHSEED'] = "random"



# Activate your virtual env
activate_env=os.path.expanduser("/home/geoevent/venv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

# import django.core.handlers.wsgi
# application = django.core.handlers.wsgi.WSGIHandler()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
