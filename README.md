# Warbler

Warbler is a Twitter clone built with Flask. PostgreSQL was used for the database and the ORM is SQLAlchemy. The frontend is served up via Jinja templating.

You can view a deployed version [here](https://http://lucas-pagac-warbler.herokuapp.com/).

## Setup Instructions

1. Clone this repository
2. Create a virtual environment
    * `python3 -m venv venv`
    * `source venv/bin/activate`
    * `pip3 install -r requirements.txt`
3. Create the database
    * `createdb warbler`
    * `createdb warbler-test`
    * `python3 seed.py`
4. Run tests:
    * To run all: `python3 -m unittest`
5. Start the server
    * `flask run`

## Technologies

  * Flask
  * Flask-WTForms
  * PostgreSQL
  * SQLAlchemy
  * Jinja
