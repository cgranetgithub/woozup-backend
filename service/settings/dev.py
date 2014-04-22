from prod import *

DEBUG = True
TEMPLATE_DEBUG = True
TASTYPIE_FULL_DEBUG = True

SECRET_KEY = '(jut!-c_9j^a==v$+6(-w4x8v#%*ljd7y3h0w-=*d5r@f5hy-z'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('storages')
INSTALLED_APPS.append('django_extensions')
INSTALLED_APPS = tuple(INSTALLED_APPS)
del STATICFILES_STORAGE
del DEFAULT_FILE_STORAGE
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

EMAIL_HOST = 'auth.smtp.1and1.fr'
EMAIL_HOST_USER = 'contact@linbees.com'
EMAIL_HOST_PASSWORD = 'sc39cf63'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
