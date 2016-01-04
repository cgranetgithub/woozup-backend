# web: gunicorn service.wsgi
web: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn service.wsgi
worker: python worker.py
