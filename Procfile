web: gunicorn rapidventa.wsgi:application --bind 0.0.0.0:$PORT --workers 4
worker: celery -A rapidventa worker --loglevel=info
beat: celery -A rapidventa beat --loglevel=info
