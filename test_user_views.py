""" User View tests. """

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Like
from bs4 import BeautifulSoup

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

        self.testuser = User.signup(
            username="testuser",
            email="test@test.com",
            password="testuser",
            image_url=None
        )
        self.testuser_id = 9999
        self.testuser.id = self.testuser_id

        self.u1 = User.signup(
            username="testuser1",
            email="test1@test.com",
            password="testuser",
            image_url=None
        )
        self.u1_id = 1111
        self.u1.id = self.u1_id

        self.u2 = User.signup(
            username="testuser2",
            email="test2@test.com",
            password="testuser",
            image_url=None
        )
        self.u2_id = 2222
        self.u2.id = self.u2_id

        self.u3 = User.signup(
            username="testuser3",
            email="test3@test.com",
            password="testuser",
            image_url=None
        )

        self.u4 = User.signup(
            username="testuser4",
            email="test4@test.com",
            password="testuser",
            image_url=None
        )

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_list(self):
        """ Does list of users display? """

        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("@testuser3", str(resp.data))
            self.assertIn("@testuser4", str(resp.data))

    def test_users_show(self):
        """ Does user profile display? """
        # TODO: Add authentication test

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))

    def setup_likes(self):
        """ Function to setup likes for following tests. """

        test_msg1 = Message(
            text="test message1",
            user_id=self.testuser_id,
        )

        test_msg2 = Message(
            text="test message2",
            user_id=self.testuser_id,
        )

        test_msg3 = Message(
            id=1234,
            text="test message3",
            user_id=self.u1_id,
        )

        db.session.add_all([test_msg1, test_msg2, test_msg3])
        db.session.commit()

        msg_liked = Like(
            user_id=self.testuser_id,
            message_id=1234,
        )

        db.session.add(msg_liked)
        db.session.commit()

    def test_messages_add_like(self):
        """ Does adding a like for currently-logged-in user work? """

        test_msg = Message(
            id=1987,
            text="test message",
            user_id=self.u1_id,
        )
        db.session.add(test_msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(
                "/messages/1987/like",
                follow_redirects=True,
            )
            self.assertEqual(resp.status_code, 200)

            msg_likes = Like.query.filter(Like.message_id == 1987).all()
            self.assertEqual(len(msg_likes), 1)
            self.assertEqual(msg_likes[0].user_id, self.testuser_id)

    def test_messages_remove_like(self):
        """ Does removing a like for currently-logged-in user work? """

        self.setup_likes()

        test_msg = Message.query.filter(
            Message.text == "test message3"
        ).one()

        self.assertIsNotNone(test_msg)
        self.assertNotEqual(
            test_msg.user_id,
            self.testuser_id,
        )

        msg_likes = Like.query.filter(
            Like.user_id == self.testuser_id and Like.message_id == test_msg.id
        ).one()

        self.assertIsNotNone(msg_likes)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(
                f"/messages/{test_msg.id}/like",
                follow_redirects=True,
            )

            self.assertEqual(resp.status_code, 200)

        msg_likes2 = Like.query.filter(
            Like.message_id == test_msg.id
        ).all()
        self.assertEqual(len(msg_likes2), 0)

    def test_messages_add_like_unauthorized(self):
        """ Unauthorized users are not able to like a message? """

        self.setup_likes()

        test_msg = Message.query.filter(
            Message.text == "test message3"
        ).one()

        self.assertIsNotNone(test_msg)

        like_count = Like.query.count()

        with self.client as c:
            resp = c.post(
                f"/messages/{test_msg.id}/like",
                follow_redirects=True,
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            self.assertEqual(like_count, Like.query.count())

    def setup_followers(self):
        """ Function to setup follows for following tests. """

        follower1 = Follows(
            user_being_followed_id=self.u1_id,
            user_following_id=self.testuser_id,
        )

        follower2 = Follows(
            user_being_followed_id=self.u2_id,
            user_following_id=self.testuser_id,
        )

        follower3 = Follows(
            user_being_followed_id=self.testuser_id,
            user_following_id=self.u1_id,
        )

        db.session.add_all([follower1, follower2, follower3])
        db.session.commit()

    def test_users_following(self):
        """ Show list of people this user is following works? """

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertNotIn("@testuser3", str(resp.data))
            self.assertNotIn("@testuser4", str(resp.data))

    # def test_users_followers(self):
    #     """ Display list of followers works? """

    # def test_users_add_follow(self):
    #     """ Does adding a follow for currently-logged-in user work? """

    # def test_users_stop_following(self):
    #     """ Does stop following for currently-logged-in user work? """

    # def test_users_edit_profile(self):
    #     """ Can the currently-logged-in user update their profile? """

    # def test_users_delete(self):
    #     """ Does deleting a user work? """
