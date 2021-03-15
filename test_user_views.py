""" User View tests. """

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        testuser = User(
            username="testuser",
            email="test@test.com",
            password="testuser",
            image_url=None
        )
        db.session.add(testuser)
        db.session.commit()

        self.test_id = testuser.id

        test_message_like_user = User(
            username="test2",
            email="test2@test.com",
            password="testuser",
            image_url=None
        )
        db.session.add(test_message_like_user)
        testmsg = Message(text="test_liked_message")
        test_message_like_user.messages.append(testmsg)
        db.session.commit()
        testuser.messages_liked.append(testmsg)
        db.session.commit()

        self.test_user_likes_id = test_message_like_user.id

    def test_users_list(self):
        """ Display list of users works? """

    def test_users_show(self):
        """ Display user profile works? """

    def test_users_following(self):
        """ Display list of people this user is following works? """

    def test_users_followers(self):
        """ Display list of followers works? """

    def test_users_add_follow(self):
        """ Does adding a follow for currently-logged-in user work? """

    def test_users_stop_following(self):
        """ Does stop following for currently-logged-in user work? """

    def test_users_edit_profile(self):
        """ Can the currently-logged-in user update their profile? """

    def test_users_delete(self):
        """ Does deleting a user work? """