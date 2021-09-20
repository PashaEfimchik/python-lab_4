from re import I
from flask import Flask
from flask_login import LoginManager, login_manager, current_user
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
import socketio

db = SQLAlchemy()
socketio = SocketIO()

from website.models import *

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

class HomeAdminView(AdminIndexView):
    def is_accessible(self):
        return not current_user.is_anonymous and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return super().inaccessible_callback(name, **kwargs)

def create_app(config="config.MyConfig"):
    app = Flask(__name__)
    app.config.from_object(config)

    init_user(app)
    
    admin.init_app(app, url='/', index_view=AdminMenu(name='Home'))
    admin.add_view(UsersView(Users, db.session))
    admin.add_view(PostsView(Posts, db.session))

    socketio.init_app(app, cors_allowed_origins='*')
    return app

def init_user(app):
    db.init_app(app)