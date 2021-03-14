# Warbler <img src="/static/images/warbler-logo.png" alt="logo" width="50" height="50"> 

Warbler is a miniature clone of the popular social messaging platform, Twitter. Warbler lets you send out messages (or "warbles") that are max 140 characters long. Users can follow/unfollow other users and like/unlike each others' messages.  

Check out the deployed app <a href="https://winnie-chou-warbler.herokuapp.com/">here</a>.

## Screenshots

Below are screenshots of the deployed app:

<span>
    <img src="/static/images/warbler-landing-page.png" width="350" height="350" border="1px" margin="10px">
    <img src="/static/images/warbler-signup-form.png" width="350" height="350" border="1px" margin="10px">
</span>
<img src="/static/images/warbler-user-profile.png" width="750" height="400">

**Database Design**

<img src="/static/images/database-er-diagram.jpg" width="1000" height="250">

- Note: The follows and likes tables are both join tables and have two foreign keys as each table's respective primary key. 
- Key relationships:
    - One user may have many messages (one-to-many)
    - One user may like many messages (one-to-many)
    - One user may have many followers and one user may be following many users (many-to-many)

## Current features
- Homepage for logged in user consists of messages from current followers, showing most recent
- Logged in user can write messages up to 140 characters long
- Logged in user can like (star) and unlike (unstar) other user's messages
- Logged in user can follow and unfollow other users
- Logged in user can search for users
- Logged in user can edit own profile

## Upcoming features
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

## Dependencies
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

**Frontend dependencies** include:
- Bootstrap
- fontawesome
- jQuery
- popper

Note: frontend dependencies use scripts, see base.html

## Installation
**App Development Setup**

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

## Testing
Tests have been created for both the models and routes (view-functions). There are four test files in total: one set of tests for users and one set of tests for messages. 

To run a file containing unittests, you can run the following command:

```console
FLASK_ENV=production python3 -m unittest <name-of-python-file>
```
We set FLASK_ENV for this command, so it doesn’t use debug mode, and therefore won’t use the Debug Toolbar during our tests. If you are having an error running tests (comment out the line in your app.py that uses the Debug Toolbar).

## Deployment
We used gunicorn for our production ready server and Heroku for deployment. To follow a similar process, you can deploy by

Create a Procfile to tell Heroku what command to run to start the server:
```console
echo "web: gunicorn app:app" > Procfile
```

Add a runtime.txt file to capture version of Python being used:
```console
echo "python-3.7.2" > runtime.txt
```

Create a Heroku app through your console:
```console
heroku login
heroku create_NAME_OF_APP
git remote -v
git push heroku master
heroku open
```

Reminder to configure and set our environment variables to production variables. 

Add and connect a Postgres database (we used the hobby-dev free tier):
```console
heroku addons:create heroku-postgresql:hobby-dev
heroku config
heroku pg:psql
```

Now you can run a SQL file on Heroku or run commands on your production server.
We seeded our database:
```console
heroku run python3 seed.py
```

## Authors
- Winnie Chou
- Lucas Pagac (pair programming partner)
