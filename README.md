# Warbler

Warbler is a miniature clone of the popular social messaging platform, Twitter. Warbler lets you send out messages (or "warbles") that are max 140 characters long. Users can follow others and like other users' messages.  

Check out the deployed app <a href="https://winnie-chou-warbler.herokuapp.com/">here</a>.

## Screenshots

TODO: TBU with application screenshots

Database:
TODO: insert diagram

- Note: The follows and likes tables are both join tables and have two foreign keys. 
- Key relationships:
    - One user may have many messages (one-to-many)
    - One user may like many messages (one-to-many)
    - One user may have many followers and one user may be following many users (many-to-many)

## Current features

- General app functions:
    - Homepage of messages from followers
    - Ability to write messages up to 140 characters long
    - Ability to like (star) and unlike (unstar) messages
    - Ability to follow and unfollow other users
    - Ability to search for users
    - Ability to edit own profile

## Upcoming features

- Additional features under development:
    - AJAX for liking / unliking messages without needing a full page refresh
    - DRY up authorization
    - DRY up URLs
    - Optimize queries
    - Make change password form
    - Allow "private" accounts
    - Add admin users
    - User blocking
    - Direct messages
    - Custom 404 page
    - DRY up templates

## Tech stack
- PostgreSQL for database
- SQLAlchemy for database ORM
- Flask/Python for backend
- JavaScript, CSS & Bootstrap for frontend

## Installing
**Backend dependencies** include:
- bcrypt
- email-validator
- Flask
- gunicorn
- Jinja2
- psycopg2-binary
- SQLALchemy
- WTForms
Note: faker library was used to generate users and messages for seeding

**Setup**
Create the Python virtual environment:
```console
python3 -m venv venv
source venv/bin/activate
(venv) $ pip3 install -r requirements.txt
```

Set up the database:
```console
(venv) createdb warbler
(venv) python3 seed.py
```

Start the server:
```console
(venv) flask run
```

**Frontend dependencies** include:
- Bootstrap
- fontawesome
- jQuery
- popper

Note: frontend dependencies use scripts, see base.html

## Testing
Tests have been created for both the models and routes (view-functions). There are four test files in total: one set of tests for users and one set of tests for messages. 

To run a file containing unittests, you can run the following command:

```console
FLASK_ENV=production python3 -m unittest <name-of-python-file>
```
We set FLASK_ENV for this command, so it doesn’t use debug mode, and therefore won’t use the Debug Toolbar during our tests. If you are having an error running tests (comment out the line in your app.py that uses the Debug Toolbar).

## Deploying
We used gunicorn for our production ready server and Heroku for deployment. 

Created Procfile to tell Heroku what command to run to start the server:
```console
echo "web: gunicorn app:app" > Procfile
```

Added a runtime.txt file to capture version of Python being used:
```console
echo "python-3.7.2" > runtime.txt
```

Created our Heroku app:
```console
heroku login
heroku create_NAME_OF_APP
git remote -v
git push heroku master
heroku open
```

Set our environment variables to production variables. 

Added and connected a Postgres database using the hobby-dev free tier:
```console
heroku addons:create heroku-postgresql:hobby-dev
heroku config
heroku pg:psql
```

Now you can run a SQL file on Heroku or run commands on your production server. We seeded our database:
```console
heroku run python3 seed.py
```


## Authors
- Winnie Chou
- Lucas Pagac (pair programming partner)
