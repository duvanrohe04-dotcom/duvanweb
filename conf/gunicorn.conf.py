import os

port = os.getenv('PORT', '5001')
bind = f'0.0.0.0:{port}'

# Worker configuration
workers = int(os.getenv('GUNICORN_WORKERS', '2'))
threads = int(os.getenv('GUNICORN_THREADS', '4'))
worker_class = 'gthread'

# Disable sendfile to prevent zero-byte transfer bug on Linux Docker/OverlayFS
sendfile = False

# Timeouts & Keepalive
timeout = 30
graceful_timeout = 10
keepalive = 5

# Memory leak prevention & auto-recycle workers
max_requests = 1000
max_requests_jitter = 50

# Request limits
limit_request_line = 8190

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')
