# Vivrelle Take Home Assessment

## Installation

This project runs on Python, Django, and Django REST Framework.
Start by creating your virtual environment

Windows:

```
python3 -m venv venv
source venv/Scripts/activate
```

Linux / Mac:

```
python3 -m venv venv
source venv/bin/activate
```

Afterwards run the following to install the requirements for the project:

```
pip install -r requirements.txt
```

## Apply Migrations

Migrate withh the following Django Command.

```
python manage.py migrate
```

## Seed the database

Seed the db3 with the following command

```
python manage.py seed_data
```

## Start the Server

Run the Django Server with the following command

```
python manage.py runserver
```

API is available at `http://127.0.0.1:8000/api/`

## Run Regression Tests

Test using

```
python manage.py test tests
```
