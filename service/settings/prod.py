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

# Admin and manager (will receive emails)
ADMINS = (
    ('charles', 'cgranet@protonmail.com'),
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
    # REST API
    'rest_framework',     # REST API
    'rest_framework.authtoken',
    'rest_auth',
    'django_filters',
    'crispy_forms',
    # allauth & REST registration
    'django.contrib.sites', # The Django sites framework is required
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    # allauth, social auth
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.instagram',
    # project apps
    'event.apps.EventConfig',
    'link.apps.LinkConfig',
    'userprofile.apps.UserProfileConfig',
    'web.apps.WebConfig',
    'journal.apps.JournalConfig'
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

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}

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
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"

# Email (sendgrid)
#EMAIL_HOST = 'smtp.sendgrid.net'
#EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "")
#EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD", "")
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True
#DEFAULT_FROM_EMAIL = "contact@woozup.social"

# SMS (plivo)
SMS_AUTH_ID = os.environ.get("PLIVO_AUTH_ID", "")
SMS_AUTH_TOKEN = os.environ.get("PLIVO_AUTH_TOKEN", "")
SMS_SENDER_PHONE = os.environ.get("PLIVO_SENDER_PHONE", "")

# PUSH NOTIFICATIONS
PUSH_NOTIFICATIONS_SETTINGS = {
    "GCM_API_KEY": os.environ.get("GCM_API_KEY", ""),
    "APNS_CERTIFICATE": os.path.join(BASE_DIR, "pushcert.pem")
}

# Cache settings.
import urlparse
redis_url = urlparse.urlparse(os.environ.get('REDISCLOUD_URL', "localhost"))
CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%s' % (redis_url.hostname, redis_url.port),
            'OPTIONS': {
                'PASSWORD': redis_url.password,
                'DB': 0,
        }
    }
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

SITE_ID = 1
