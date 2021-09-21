from re import I
from flask import Flask
from flask_login import current_user, LoginManager, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()

from website.models import *

login_manager = LoginManager()
login_manager.login_view = "users.login"
admin = Admin()

class AdminMenu(AdminIndexView):
    def is_accessible(self):
        return super().is_accessible()

    def inaccessible_callback(self, name, **kwargs):
        return super().inaccessible_callback(name, **kwargs)

class UsersView(ModelView):
    column_list = ['id', 'email', 'username', 'password', 'is_admin']

class PostsView(ModelView):
    column_list = ['id', 'post_time', 'title', 'content']

def create_app(config="config.MyConfig"):
    app = Flask(__name__)
    app.config.from_object(config)
    init_user(app)

    admin.init_app(app, url='/', index_view=AdminMenu(name='Home'))
    admin.add_view(UsersView(Users, db.session))
    admin.add_view(PostsView(Posts, db.session))

    return app

def init_user(app):
    db.init_app(app)

    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
