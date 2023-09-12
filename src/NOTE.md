# Note

### Migrate from existing database

- Run migrations

```
python manage.py makemigrations api_orm
```

- Run migrate with `--fake-initial` option

**--fake-initial**
> Allows Django to skip an app’s initial migration if all database tables with the names of all models created by all 
> CreateModel operations in that migration already exist. 
> This option is intended for use when first running migrations against a database 
> that preexisted the use of migrations. 
> This option does not, however, check for matching database schema beyond matching table names 
> and so is only safe to use if you are confident that your existing schema matches 
> what is recorded in your initial migration.
```
python manage.py migrate --fake-initial
```

