#import flask_testing
import unittest
import flask
import pytest
from flask.app import Flask
from website.models import Users
from flask_testing import TestCase
from website import create_app, db
from app import app as myapp

class MyTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

def test_flask_simple():
    app = Flask(__name__)
    app.config['TESTING'] = True
    user = app.test_client()
    result = user.get('/')
    
#myapp = flask.Flask(__name__)

class Test(unittest.TestCase):
    def setUp(self):
        self.app = myapp.test_client()
    
    #def test_index(self):
        #rv = self.app.get('/index')
        #assert rv.status == '200 OK'
        #self.assertEqual(rv.status, '200 OK')

    def test_home(self):
        tester = myapp.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        

    def test_login(self):
        tester = myapp.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        tester = myapp.test_client(self)
        response = tester.get('/register', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_other(self):
        tester = myapp.test_client(self)
        response = tester.get('a', content_type='html/text')
        self.assertEqual(response.status_code, 404)
        
    def test_members(self):
        tester = myapp.test_client(self)
        response = tester.get('/index', content_type='html/text')
        self.assertEqual(response.status_code, 404)

    def test_404(self):
        rv = self.app.get('/other')
        self.assertEqual(rv.status, '404 NOT FOUND')
    
    def register(self, username, password):
        return self.app.post('/register', data=dict(
        username=username,
        password=password
        ), follow_redirects=True)

    def test_register_messages(self):
        """Test register messages using helper functions."""
        rv = self.register(
             "admin",
                ""
        )
        #assert b'Password is required' in rv.data
        rv = self.register(
                "",
                "admin"
        )
        #assert b'Username is required' in rv.data

#class SomeTest(MyTest):

    #def test_something(self):
        #user = Users("admin", "admin@example.com", "admin")
        #db.session.add(user)
        #db.session.commit()
        #assert user in db.session
        #response = self.client.get("/login")
        #assert user in db.session


if __name__ == '__main__':
  unittest.main()