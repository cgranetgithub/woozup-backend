# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# __file__ = BASE_DIR/service/settings/prod.py

# SECURITY WARNING: keep the secret key used in production secret!
from django.utils.crypto import get_random_string
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

SITE_ID = 1

# Admin and manager (will receive emails)
ADMINS = (
    ('charles', 'charles@varioware.com'),
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
    #
    'corsheaders',        # CORS
    'tastypie',           # REST API
    'storages',           # S3 storage
    'push_notifications', # push to mobile
    # `allauth`
    'django.contrib.sites', # The Django sites framework is required
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.instagram',
    'allauth.socialaccount.providers.linkedin',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.soundcloud',
    'allauth.socialaccount.providers.spotify',
    'allauth.socialaccount.providers.tumblr',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.vimeo',
    # project apps
    'event',
    'link',
    'userprofile',
    'web'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                 # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
            'debug': DEBUG,
        },
    },
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

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
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
from s3_storage import *

# allauth configuration
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Woozup - "
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# Email
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "")
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD", "")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "contact@woozup.social"

# GeoDjango
GEOS_LIBRARY_PATH = "{}/libgeos_c.so".format(environ.get('GEOS_LIBRARY_PATH'))
GDAL_LIBRARY_PATH = "{}/libgdal.so".format(environ.get('GDAL_LIBRARY_PATH'))
PROJ4_LIBRARY_PATH = "{}/libproj.so".format(environ.get('PROJ4_LIBRARY_PATH'))

# PUSH NOTIFICATIONS
PUSH_NOTIFICATIONS_SETTINGS = {
    "GCM_API_KEY": os.environ.get("GCM_API_KEY", ""),
    "APNS_CERTIFICATE": os.path.join(BASE_DIR, "pushcert.pem")
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
