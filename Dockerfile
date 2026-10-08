FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/duvan_web.db

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /data

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD python -c "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','5001')+'/health')" || exit 1

CMD ["gunicorn", "--conf", "conf/gunicorn.conf.py", "app:create_app()"]
