python3 manage.py migrate
gunicorn --bind=0.0.0.0 --reload --log-level DEBUG --timeout 600 django_gui.wsgi:application &
celery -A django_gui worker --loglevel=DEBUG
