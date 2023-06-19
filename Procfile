web: gunicorn django_gui.wsgi --log-file -
worker: celery worker -A django_gui -l info
