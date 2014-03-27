import os

# Use Amazon S3 for storage for uploaded media files.
DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

# Use Amazon S3 for static files storage.
#STATICFILES_STORAGE = "require_s3.storage.OptimizedCachedStaticFilesStorage"
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Amazon S3 settings.
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")
AWS_AUTO_CREATE_BUCKET = True
AWS_HEADERS = {
    "Cache-Control": "public, max-age=86400",
}
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = False
AWS_REDUCED_REDUNDANCY = False
AWS_IS_GZIPPED = False

STATIC_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3-website-eu-west-1.amazonaws.com/'

#ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
