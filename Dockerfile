# FROM python:3.10-alpine

FROM python:3.12.12-alpine

WORKDIR /app

# RUN apk update && apk add --no-cache gcc musl-dev mysql-dev git shadow
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    mysql-dev \
    git \
    shadow \
    cairo-dev \
    cairo \
    pango-dev \
    gdk-pixbuf-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    curl

RUN groupadd -r cystack && useradd -r -g cystack -s /usr/sbin/nologin -c "CyStack user" cystack

RUN pip install --upgrade pip

RUN pip install wheel==0.45.1

COPY requirements.txt ./

RUN pip install -r requirements.txt

EXPOSE 8000

COPY . /app

RUN mkdir media

RUN chown -R cystack: media

USER cystack

ENV PROD_ENV prod

CMD python manage.py migrate; gunicorn -w 3 -t 120 -b 0.0.0.0:8000 server_config.wsgi:application & daphne -b 0.0.0.0 -p 8001 server_config.asgi:application || true

#  || true & python cron_task.py || true

# & python manage.py rqworker default || true
