"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

import os
from unittest import TestCase
from models import db, Message, User
from app import app, CURR_USER_KEY

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app


app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.u1 = User(
            username="testuser1",
            email="test@test.com",
            password="testuser",
            image_url=None
        )
        db.session.add(self.u1)

        self.u2 = User(
            username="testuser2",
            email="test2@test.com",
            password="testuser",
            image_url=None
        )
        db.session.add(self.u2)

        self.testmsg = Message(text="test_liked_message")
        self.u2.messages.append(self.testmsg)
        self.u1.messages_liked.append(self.testmsg)

        db.session.commit()

        self.u1_id = self.u1.id
        self.u2_id = self.u2.id

    def test_message_add(self):
        """ With session, can currently-logged-in user add a message? """

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post(
                "/messages/new",
                data={"text": "Hello"},
                )

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter_by(text="Hello").first()
            self.assertEqual(msg.text, "Hello")

            resp = c.post(
                "/messages/new",
                data={"text": "Hello"},
                follow_redirects=True,
                )
            html = resp.get_data(as_text=True)

            # Make sure redirect follows through
            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="users-show-page"', html)
            self.assertIn("Hello", html)

    def test_message_add_no_session(self):
        """ Without session, currently-logged-in user cannot add a message? """

        with self.client as c:
            resp = c.post(
                "messages/new",
                data={"test": "Hello"},
                follow_redirects=True,
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_message_add_invalid_user(self):
        """ Invalid user cannot add a message? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 92347984536  # user does not exist

            resp = c.post(
                "messages/new",
                data={"test": "Hello"},
                follow_redirects=True,
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_message_show(self):
        """ With session, are currently-logged-in user's messages shown? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            test_msg = Message(
                text="test_message",
                user_id=self.u1_id,
            )

            db.session.add(test_msg)
            db.session.commit()

            resp = c.get(f"/messages/{test_msg.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(test_msg.text, str(resp.data))
            self.assertNotIn('Hello', html)
            self.assertIn('id="message-show-page"', html)

            msg = Message.query.get(test_msg.id)
            self.assertEqual(msg.text, "test_message")

    def test_message_show_invalid(self):
        """ 404 error if trying to access a message that does not exist? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/messages/93185742058")

            self.assertEqual(resp.status_code, 404)

    def test_message_destroy(self):
        """ With session, can currently-logged-in user delete a message? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            test_msg = Message(
                text="test_message",
                user_id=self.u1_id,
            )
            db.session.add(test_msg)
            db.session.commit()

            msg = Message.query.all()
            self.assertEqual(len(msg), 2)

            # Delete added message
            resp = c.post(f"/messages/{test_msg.id}/delete")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            msg = Message.query.all()
            self.assertEqual(len(msg), 1)

            # Add a second message
            test_msg2 = Message(
                text="test_message",
                user_id=self.u1_id,
            )
            db.session.add(test_msg2)
            db.session.commit()

            # Test redirect follows through
            resp = c.post(
                f"/messages/{test_msg2.id}/delete",
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="users-show-page"', html)
            self.assertNotIn("test_message", html)

    def test_message_destroy_no_session(self):
        """ Without session, cannot delete a message? """

        test_msg = Message(
            id=1234,
            text="test_message",
            user_id=self.u1.id,
        )
        db.session.add(test_msg)
        db.session.commit()

        with self.client as c:
            resp = c.post(
                "/messages/1234/delete",
                follow_redirects=True,
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            test_msg = Message.query.get(1234)
            self.assertIsNotNone(test_msg)

    def test_message_destroy_unauthorized(self):
        """ Unauthorized user (user does not own message) cannot delete? """

        unauth_user = User.signup(
            username="test-unauthorized",
            email="test-unauth@test.com",
            password="testuser",
            image_url=None,
        )

        # message belongs to testuser1
        test_msg = Message(
            id=1234,
            text="test_message",
            user_id=self.u1.id,
        )
        db.session.add_all([unauth_user, test_msg])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = unauth_user.id

            resp = c.post(
                "/messages/1234/delete",
                follow_redirects=True,
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            msg = Message.query.get(1234)
            self.assertIsNotNone(msg)

    def test_messages_liked_list(self):
        """ Does list of messages liked get displayed? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/likes")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="liked-messages-page"', html)
            self.assertIn('test_liked_message', html)
            self.assertNotIn('test_message', html)
