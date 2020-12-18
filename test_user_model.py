"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app
from sqlalchemy.exc import IntegrityError
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(self.u)
        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u.messages), 0)
        self.assertEqual(len(self.u.followers), 0)
        self.assertIn("test@test.com", repr(self.u))

    def test_user_follow_methods(self):
        """ Do is_following and is_followed_by work? """   

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
        )
        db.session.add(u2)
        db.session.flush()

        self.u.followers.append(u2)
        self.u.following.append(u2)
        db.session.commit()

        self.assertEqual(self.u.is_following(u2), True)
        self.assertEqual(self.u.is_followed_by(u2), True)
        self.u.following.remove(u2)
        self.u.followers.remove(u2)
        db.session.commit()
        self.assertEqual(self.u.is_followed_by(u2), False)
        self.assertEqual(self.u.is_followed_by(u2), False)

    def test_user_signup(self):
        """ Does User.signup method work? """ 

        user_signup_test = User.signup(
            "signup_test",
            "signup@test.com",
            "HASHED_PASSWORD",
            None
        )
        db.session.commit()
        self.assertIsInstance(user_signup_test, User)

        User.signup(
            "signup_test",
            "signup_invalid@test.com",
            "HASHED_PASSWORD",
            None
        )
        try:
            db.session.commit()
        except IntegrityError:
            error = True

        self.assertTrue(error)

    def test_user_authenticate(self):
        """ Does User.authenticate work? """

        user_signup = User.signup(
            "signup_test",
            "signup@test.com",
            "HASHED_PASSWORD",
            None
        )
        db.session.add(user_signup)
        db.session.commit()
        user_authenticate = User.authenticate("signup_test", "HASHED_PASSWORD")
        self.assertIs(user_authenticate, user_signup)

        self.assertFalse(User.authenticate('signup_test', "Invalid password"))
        self.assertFalse(User.authenticate('Invalid_username', "HASHED_PASSWORD"))

    def test_user_messages_liked(self):
        """ Does messages_liked relationship work? """

        new_user = User.signup(
            "rel_test",
            "rel_test@test.com",
            "HASHED_PASSWORD",
            None,
        )
        db.session.commit()
        print("new user = ", new_user)
        message = Message(
            text="This is a test message.",
        )
        print("new message =", message)
        self.u.messages.append(message)
        db.session.flush()
        new_user.messages_liked.append(message)
        db.session.commit()
        print("messages liked =", new_user.messages_liked)

        self.assertIn(message, new_user.messages_liked)
        self.assertIn(new_user, message.users_who_liked)
