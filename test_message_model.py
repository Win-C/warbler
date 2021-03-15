"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.u = User(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url=None,
        )

        db.session.add(self.u)

        self.m = Message(
            text="This is a test message.",
        )

        self.u.messages.append(self.m)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        self.assertIn("This is a test message.", self.m.text)
        self.assertEqual(self.m.user_id, self.u.id)
        self.assertEqual(self.m.user.id, self.u.id)
