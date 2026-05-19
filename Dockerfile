FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --force-reinstall psycopg[binary] psycopg2-binary

COPY . .

EXPOSE 5001

CMD ["gunicorn", "--conf", "conf/gunicorn.conf.py", "app:create_app()"]
