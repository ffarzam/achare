FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN pip install --upgrade pip

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/


CMD python manage.py collectstatic --no-input && \
    python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py runserver 0.0.0.0:8000


