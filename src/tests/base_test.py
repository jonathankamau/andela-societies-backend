"""Module to house setup, teardown and utility class for testing."""


import os
import datetime
import base64
from unittest import TestCase

from api.models import (Activity, ActivityType, Cohort, Country,
                        LoggedActivity, Society, User, db)
from app import create_app
from jose import jwt


class BaseTestCase(TestCase):
    """Contain utility required for testing."""

    exp_date = datetime.datetime.utcnow()
    test_payload = {
        "UserInfo": {
            "email": "test.test@andela.com",
            "first_name": "test",
            "id": "-Ktest_id",
            "last_name": "test",
            "name": "test test",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Fellow": "-Ktest_fellow_id"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    expired_payload = {
        "UserInfo": {
            "email": "test.test@andela.com",
            "first_name": "test",
            "id": "-Ktest_id",
            "last_name": "test",
            "name": "test test",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Fellow": "-Ktest_fellow_id"
            }
        },
        "exp": exp_date + datetime.timedelta(seconds=1)
    }

    incomplete_payload = {
        "UserInfo": {
            "first_name": "test",
            "last_name": "test",
            "name": "test test",
            "picture": "https://www.link.com",
            "roles": {
                    "Andelan": "-Ktest_andelan_id",
                    "Fellow": "-Ktest_fellow_id"
            }
        },
        "exp": exp_date + datetime.timedelta(days=1)
    }

    def setUp(self):
        """Setup function to configure test enviroment."""
        self.app = create_app("Testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

        # test client
        self.client = self.app.test_client()

        self.header = {
            "Authorization": self.generate_token(self.test_payload)
        }
        self.bad_token_header = {
            "Authorization": self.generate_token(
                {"I don't know": "what to put here"}
            )
        }

        # test countries
        self.kenya = Country(name='Kenya')
        self.uganda = Country(name='Uganda')
        self.nigeria = Country(name='Nigeria')

        # test societies
        self.phoenix = Society(name="Phoenix")
        self.istelle = Society(name="iStelle")
        self.sparks = Society(name="Sparks")
        self.invictus = Society(name="Invictus")

        # test cohorts
        self.cohort_12_Ke = Cohort(name="cohort-12", country=self.kenya)
        self.cohort_12_Ug = Cohort(name="cohort-12", country=self.uganda)
        self.cohort_1_Nig = Cohort(name="cohort-1", country=self.nigeria)

        # test Users
        self.test_user = User(
            uuid="-KdQsMt2U0ixIy_-yWTSZ",
            name="Test User",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAAAABc/ImM13eP_cAI/photo.jpg?sz=50",
            email="test.user@andela.com",
            country=self.nigeria,
            cohort=self.cohort_1_Nig,
            society = self.phoenix)

        self.test_user_2 = User(
            uuid="-KdQsawesome_useridZ",
            name="Test User 2",
            photo="https://lh6.googleusercontent.com/-1DhBLOJentg/AAAAAAAAA"
                  "AI/AAAAAAAAABc/ImM13eP_cAI/photo.jpg?sz=50",
            email="test.user2@andela.com",
            country=self.nigeria,
            cohort=self.cohort_12_Ke,
            society=self.sparks)

        # test ActivityType
        self.hackathon = ActivityType(name="Hackathon",
                                      description="A Hackathon",
                                      value=100)
        self.tech_event = ActivityType(name="Tech Event",
                                       description="Organize a tech event",
                                       value=2500)
        self.tech_event.save()

        # test Activity
        self.alibaba_ai_challenge = Activity(name='Fashion challenge',
                                             activity_type=self.hackathon)
        self.js_meet_up = Activity(name='Nairobi Js meetup',
                                   activity_type=self.tech_event)

        # test LoggedActivity
        self.log_alibaba_challenge = LoggedActivity(
            name="my logged activity",
            description="Participated in this event",
            value=2500,
            user=self.test_user,
            activity=self.alibaba_ai_challenge,
            society=self.phoenix,
            activity_type=self.hackathon
        )

    @staticmethod
    def generate_token(payload):
        """Generate token."""
        env_key = os.environ['PRIVATE_KEY_TEST']
        decoded_key = base64.b64decode(env_key).decode("utf-8")
        token = jwt.encode(payload, decoded_key, algorithm="RS256")
        return token

    def tearDown(self):
        """Clean up after every test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()