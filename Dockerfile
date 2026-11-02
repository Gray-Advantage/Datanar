FROM python:3.13.17-alpine

RUN apk add --no-cache gettext

COPY ./requirements /requirements
RUN pip install --no-cache-dir -r requirements/dev.txt
RUN rm -rf requirements

COPY ./datanar /datanar/
WORKDIR /datanar

CMD python manage.py makemigrations \
 && python manage.py migrate \
 && python manage.py init_superuser \
 && python manage.py init_site \
 && python manage.py compilemessages \
 && python manage.py collectstatic --no-input \
 && gunicorn datanar.wsgi:application \
    --workers $(nproc) \
    --bind 0.0.0.0:8000 \
    --access-logfile /datanar/logs/gunicorn_access.log \
    --error-logfile /datanar/logs/gunicorn_error.log