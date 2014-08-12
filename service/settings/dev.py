from prod import *

DEBUG = True
TEMPLATE_DEBUG = True
TASTYPIE_FULL_DEBUG = True

SECRET_KEY = '(jut!-c_9j^a==v$+6(-w4x8v#%*ljd7y3h0w-=*d5r@f5hy-z'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geoevent',
        'USER': 'testdjango',
        'PASSWORD': 'test',
        'HOST': 'localhost',
        'PORT': '',
    }
}

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('storages')
#INSTALLED_APPS.append('django_extensions')
INSTALLED_APPS.append('tastypie_swagger') # for API doc
INSTALLED_APPS = tuple(INSTALLED_APPS)
del STATICFILES_STORAGE
del DEFAULT_FILE_STORAGE
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

EMAIL_HOST = 'auth.smtp.1and1.fr'
EMAIL_HOST_USER = 'contact@linbees.com'
EMAIL_HOST_PASSWORD = 'pwd'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

TASTYPIE_SWAGGER_API_MODULE = 'service.urls.v1_api'
