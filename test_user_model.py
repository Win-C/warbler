"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

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

        self.u1 = User(
            username="testuser1",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url=None,
        )

        self.u2 = User(
            username="testuser2",
            email="test2@test.com",
            password="HASHED_PASSWORD",
            image_url=None,
        )

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertIn("test@test.com", repr(self.u1))

    def test_user_follow_methods(self):
        """ Do is_following and is_followed_by work? """

        self.u1.followers.append(self.u2)
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(self.u1.is_following(self.u2), True)
        self.assertEqual(self.u1.is_followed_by(self.u2), True)

        self.u1.following.remove(self.u2)
        self.u1.followers.remove(self.u2)
        db.session.commit()

        self.assertEqual(self.u1.is_followed_by(self.u2), False)
        self.assertEqual(self.u1.is_followed_by(self.u2), False)

    def test_valid_signup(self):
        """ Does User.signup method work? """

        user_signup_test = User.signup(
            "signup_test",
            "signup@test.com",
            "HASHED_PASSWORD",
            None
        )
        db.session.commit()

        self.assertIsInstance(user_signup_test, User)
        self.assertEqual(user_signup_test.username, "signup_test")
        self.assertEqual(user_signup_test.email, "signup@test.com")
        self.assertTrue(user_signup_test.password.startswith("$2b$"))

    def test_invalid_username(self):
        """ Does User.signup method throw an error with invalid username? """

        User.signup(
            None,
            "signup_invalid@test.com",
            "HASHED_PASSWORD",
            None
        )

        try:
            db.session.commit()
        except exc.IntegrityError:
            error = True

        self.assertTrue(error)

    def test_invalid_email(self):
        """ Does User.signup method throw an error with invalid email? """

        User.signup(
            "signup_test",
            None,
            "HASHED_PASSWORD",
            None
        )

        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_invalid_password(self):
        """ Does User.signup method throw an error with invalid password? """

        with self.assertRaises(ValueError):
            User.signup(
                "signup_test",
                "signup_test@test.com",
                "",
                None
            )

        with self.assertRaises(ValueError):
            User.signup(
                "signup_test",
                "signup_test@test.com",
                None,
                None
            )

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

        self.assertFalse(
            User.authenticate('signup_test', "Invalid password")
        )
        self.assertFalse(
            User.authenticate('Invalid_username', "HASHED_PASSWORD")
        )

    def test_user_messages_liked(self):
        """ Does messages_liked relationship work? """

        message = Message(
            text="This is a test message.",
        )

        self.u1.messages.append(message)
        self.u2.messages_liked.append(message)
        db.session.commit()

        self.assertIn(message, self.u2.messages_liked)
        self.assertIn(self.u2, message.users_who_liked)
