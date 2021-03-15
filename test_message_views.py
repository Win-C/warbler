"""Message View tests."""

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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    def test_message_add(self):
        """Can user add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_id

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

    def test_message_show(self):
        """ Does message show? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_id

            testmsg = Message(text="test_message")
            testuser = User.query.get(self.test_id)
            testuser.messages.append(testmsg)
            db.session.commit()

            resp = c.get(f"/messages/{testmsg.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test_message', html)
            self.assertNotIn('Hello', html)
            self.assertIn('id="message-show-page"', html)

            msg = Message.query.get(testmsg.id)
            self.assertEqual(msg.text, "test_message")

    def test_message_destroy(self):
        """ Does message destroy? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_id

            testmsg = Message(text="test_message")
            testuser = User.query.get(self.test_id)
            testuser.messages.append(testmsg)
            db.session.commit()

            msg = Message.query.all()
            self.assertEqual(len(msg), 2)

            resp = c.post(f"/messages/{testmsg.id}/delete")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            msg = Message.query.all()
            self.assertEqual(len(msg), 1)

            testmsg2 = Message(text="test_message")
            testuser = User.query.get(self.test_id)
            testuser.messages.append(testmsg2)
            db.session.commit()

            resp = c.post(
                f"/messages/{testmsg2.id}/delete",
                follow_redirects=True,
                )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="users-show-page"', html)
            self.assertNotIn("test_message", html)

    def test_messages_liked_list(self):
        """ Does list of messages liked get displayed? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_id

            resp = c.get('/messages/liked')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="liked-messages-page"', html)
            self.assertIn('test_liked_message', html)
            self.assertNotIn('test_message', html)

    def test_message_like(self):
        """ Does liking a message work? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_id

            testmsg = Message(text="new_message_liked")
            test_user2 = User.query.get(self.test_user_likes_id)
            test_user2.messages.append(testmsg)
            db.session.commit()

            resp = c.post(f"/messages/{testmsg.id}/like")

            self.assertEqual(resp.status_code, 302)
            curr_user = User.query.get(self.test_id)
            self.assertIn(testmsg, curr_user.messages_liked)

            resp = c.post(
                f"/messages/{testmsg.id}/like",
                follow_redirects=True
                )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="liked-messages-page"', html)
            self.assertIn('new_message_liked', html)
            self.assertIn('test_liked_message', html)
            self.assertNotIn('test_message', html)

    def test_message_unlike(self):
        """ Does unliking a message work? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_id
