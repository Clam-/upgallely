# upgallely
An 'uploader' and image gallery thing turbo deluxe edition

```
scripts/install
scripts/run
```

## Alembic regrets
https://python-gino.org/docs/en/1.0/how-to/alembic.html#apply-migration-on-db
```
venv\Scripts\alembic revision -m "your migration description" --autogenerate --head head
venv\Scripts\alembic upgrade head
```
