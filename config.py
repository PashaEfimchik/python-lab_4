from re import DEBUG

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'secret key qwerty 123'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

class MyConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/my_db'
    

class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:rootpassword@localhost/test_db'
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://mydb:qwerty123@db/my_db'
