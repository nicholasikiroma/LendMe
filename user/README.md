# User Management Service

## Description

Handles operations on users.

## Usage

Create & activate virtual environment:

```bash
virtualenv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create .env file with the following variables:

```text
DATABASE_URL= <replace with your database url>
JWT_SECRET_KEY= <replace with your secret key>
```

Make database migrations:

```bash
flask db init
flask db migrate -m 'Initial migration'
flask db upgrade
```

Run Flask app:

```bash
flask run --debug --port=5001
```
