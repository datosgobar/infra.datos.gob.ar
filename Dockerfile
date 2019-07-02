FROM python:3.7-alpine3.9

ARG requirements=requirements.txt

ENV TZ=America/Argentina/Buenos_Aires \
    BASE_DIR=/app/ \
    PYTHON_VENV_DIR=/app/venv/ \
    PYTHONUNBUFFERED=1 \
    MEDIA_ROOT=/app/code/media/ \
    STATIC_ROOT=/app/code/static/ \
    APP_DIR=/app/code/ \
    APP_USER=webapp \
    DJANGO_SETTINGS_MODULE=conf.settings.production

WORKDIR $APP_DIR

COPY requirements/ requirements/
COPY requirements.txt manage.py $APP_DIR

RUN apk add --no-cache imagemagick zlib-dev jpeg-dev build-base postgresql-dev tzdata && \
    cp "/usr/share/zoneinfo/$TZ" /etc/localtime && \
    echo "$TZ" > /etc/timezone && \
    apk add --no-cache git gcc libc-dev --virtual build && \
    mkdir $APP_DIR $MEDIA_ROOT $STATIC_ROOT -p && \
    addgroup -S $APP_USER && \
    adduser -D -H -S $APP_USER $APP_USER && \
    chown $APP_USER:$APP_USER -Rc $BASE_DIR && \
    python3 -m pip install --no-cache -r $requirements && \
    apk del --no-cache build

USER $APP_USER

COPY conf conf/
COPY infra infra/

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
