from website import socketio
from flask import request
from flask_login import current_user
from flask_socketio import join_room
from website.models import *
import threading
import json

@socketio.on('join')
def join(json):
    join_room(str(json['id']), sid=json['sid'])

@socketio.on('connect')
async def connect():
    if current_user.is_anonymous:
        return False
        
    print(f'connected: {current_user.username}')
    
    post = Posts(text=json(['posts'], user=current_user, date=datetime.now()))

    for post in current_user.posts:
        join_room(str(post.id))
    
    threads = [threading.Thread(target=Posts.append(post))]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    current_user.sid = request.sid
    await db.session.commit()
    

@socketio.on('disconnect')
async def disconnect():
    print(f'disconnected: {current_user.username}')
    
    current_user.sid = None
    
    await db.session.commit()