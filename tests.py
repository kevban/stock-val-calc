from unittest import TestCase
from app import app
from models import db

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///stockval_test'

db.drop_all()
db.create_all()


class AppTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        db.session.rollback()

    def test_homepage(self):
        with app.test_client() as client:
            res = client.get('/')
            self.assertEqual(res.status_code, 200)