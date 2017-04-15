# monki

Source code for [xchan.pw](https://xchan.pw/) based on [Django](https://www.djangoproject.com/)

## Requirements

* Python 3.5+
* PostgreSQL is recommended but it should work in any database supported by Django's ORM
* Node.js

## Installation

    $ cp .env-example .env
    $ python3.6 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    $ python manage.py migrate
    $ python manage.py createsuperuser
    $ python manage.py runserver
