# Working with database
## Quick references
1. Specifics about PostgreSQL: https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes
2. Django's built-in authentication: https://docs.djangoproject.com/en/5.0/topics/auth/default/
3. Django's DB tutorial https://docs.djangoproject.com/en/5.0/intro/tutorial02/
4. Django's DB API overview https://docs.djangoproject.com/en/5.0/topics/db/queries/

## Initial setup
### Installing required packages
Run:
```bash
pip install -r requirements.txt
```
This installs all the dependencies required to run the application. Specifically, `psycopg2` (PostgreSQL database adapter for Python) is required in addition to the Django package to access PostgreSQL using Django.

### Installing the DB
In order to set up environments for working with database, you must have a PostgreSQL instance running locally.

One way this can be done is by running the docker-compose.yml file that is present in the repository's root folder. To start, simply run:
```bash
docker-compose -f .\docker-compose.yml up
```

When run, this starts up an instance of PostgreSQL and a useful utility called `Adminer`, which is a web-based graphical interface for managing DBs.

By default, the Postgres will run on port 5432 and Adminer on http://localhost:8080. The default admin account is:
```none
ID: postgres
PW: mysecretpassword
```

Alternatively, download one from https://www.postgresql.org/download/. and set it up manually.

Note that the password is set to something (obviously) very secure (that is, not at all). If you would like to change the above settings, one must:
1. Change the DB's default ID and/or Password. This is configurable by setting the `POSTGRES_PASSWORD` and the `POSTGRES_USER` environment variable in the `docker-compose.yml` file.
2. In `mysite/mysite/settings.py`, Change the hard-coded ID/PW to the new combination.

Ideally, in production, the secrets should not be hard-coded into the config file, rather, it should be read from the environment variable to prevent accidentally committing the secrets.

### Setting up the DB

Now that the DB is up and running, we need to create a new database that Django uses to store its data. 

The easiest way to do this is to use the aforementioned Adminer tool.
1. Browse to https://localhost:8080
2. Set the System to `PostgreSQL`, enter the correct username (defaults to `postgres`) and the password (defaults to `mysecretpassword`). Click Login.
3. Click `Create database`. At the moment, the database name must be `capstone-db` (this can be changed by editing `NAME` in `mysite/mysite/settings.py`).

### Applying migrations to the DB
With the DB running and configured, now you can apply the migrations to the DB. Run:
```bash
python manage.py migrate
```

This will create the necessary tables on the above database for Django to work correctly.

### Creating the Superuser for Django's admin panel

Django provides an admin panel that allows developers to manage users. However, you must create a superuser account beforehand to actually log into the panel. This can be done by running: 
```bash
python manage.py createsuperuser
```
When run, this script will prompt you for a new username and such. (Only the username and the password are required). Use the created account to log into the admin panel (http://127.0.0.1:8000/admin/).

## Working with models
Django provides the tools to enable us to define models in Python, provide necessary mappings to the DBMS in use, and generate and and apply 'migrations' to the DB when changes are made to the models.

Steps to update models are:
1. Make changes to models.py
2. Create migrations:
```bash
python manage.py makemigrations users
```
(Here, `users` is the project name - change as necessary.)

3. Applying migrations:
```bash
python manage.py migrate
```
The migrations generated can be found in `mysite/users/migrations`. While it is normally unnecessary to make manual changes to the migrations, one may have to make manual changes if changes cannot be handled automatically.

## Notes

By default, Django includes a numeric ID when creating new models, used as a primary key.

For storing user data, Django conveniently has mechanisms built in to handle user permissions and authentication - see django.contrib.auth.models.user.
https://docs.djangoproject.com/en/5.0/topics/auth/default/


However it is also a good practice to create a custom user model for futureproofing (in case we need to add further fields to the user model), which has been done here already.
(See https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#specifying-a-custom-user-model)