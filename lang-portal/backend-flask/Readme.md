## Setting up the database

Venv setup:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt
```

```sh
invoke init-db
```

This will do the following:
- create the words.db (Sqlite3 database)
- run the migrations found in `seeds/`
- run the seed data found in `seed/`

Please note that migrations and seed data is manually coded to be imported in the `lib/db.py`. So you need to modify this code if you want to import other seed data.

## Clearing the database

Simply delete the `words.db` to clear entire database.

## Running the backend api

```sh
python app.py 
```

This should start the flask app on port `8000`

## Running the API tests

```sh
cd lang-portal.
make start backend
pip install -r requirements-test.txt
pytest tests
```