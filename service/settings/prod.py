# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
from django.utils.crypto import get_random_string
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

# Admin and manager (will receive emails)
ADMINS = (
    ('charles', 'c.granet@gmail.com'),
    ('michael', 'murlock42@gmail.com'),
)
MANAGERS = ADMINS

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'social.apps.django_app.default',
    'corsheaders',        # CORS
    'tastypie',           # REST API
    'storages',           # S3 storage
    'push_notifications', # push to mobile
    'event',
    'link',
    'userprofile',
)

#TEMPLATE_CONTEXT_PROCESSORS = (
    #'django.contrib.auth.context_processors.auth',
    #'django.core.context_processors.debug',
    #'django.core.context_processors.i18n',
    #'django.core.context_processors.media',
    #'django.core.context_processors.static',
    #'django.core.context_processors.tz',
    #'django.contrib.messages.context_processors.messages',
    #'social.apps.django_app.context_processors.backends',
    #'social.apps.django_app.context_processors.login_redirect',
#)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
            'debug': DEBUG,
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/home/'
SOCIAL_AUTH_LOGIN_URL = '/'

SOCIAL_AUTH_FACEBOOK_KEY = '598322736976845'
SOCIAL_AUTH_FACEBOOK_SECRET = '13773b1fdffccfeb293e7463fa258513'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'service.urls'

WSGI_APPLICATION = 'service.wsgi.application'

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {'default' :  dj_database_url.config() }
#DATABASES['default'] =  dj_database_url.config()
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
from s3_storage import *

#TEMPLATE_DIRS = (
    #os.path.join(BASE_DIR, 'templates'),
#)
#LOCALE_PATHS = (
    #os.path.join(BASE_DIR, 'locale'),
#)

# Email
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "")
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD", "")
EMAIL_PORT = 25
EMAIL_USE_TLS = False

# GeoDjango
GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')
GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')

# Notification to mobiles
PUSH_NOTIFICATIONS_SETTINGS = {
        "GCM_API_KEY": os.environ.get("GCM_API_KEY", ""),
        #"APNS_CERTIFICATE": "/path/to/your/certificate.pem",
        }

# Cache settings.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    # Long cache timeout for staticfiles, since this is used heavily by the optimizing storage.
    "staticfiles": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 60 * 24 * 365,
        "LOCATION": "staticfiles",
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
        }
    }
}
