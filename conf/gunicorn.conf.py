import os

port = os.getenv('PORT', '5001')
bind = f'0.0.0.0:{port}'

# Worker configuration
workers = int(os.getenv('GUNICORN_WORKERS', '2'))
threads = int(os.getenv('GUNICORN_THREADS', '4'))
worker_class = 'gthread'

# Timeouts & Keepalive
timeout = 30
graceful_timeout = 10
keepalive = 5

# Memory leak prevention & auto-recycle workers
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')
