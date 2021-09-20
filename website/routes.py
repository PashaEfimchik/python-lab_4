from website.models import Users, Posts, PostForm
from website import create_app

from flask import render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
from website import db
from flask_login import login_user, current_user
from flask_toastr import Toastr
import logging

#logging.basicConfig(filename='app.log', level=logging.INFO,
#                    format='%(levelname)s:%(message)s')

app = create_app("config.MyConfig")

toastr = Toastr(app)

@app.route('/')
async def index():
    page = request.args.get('page', 1, type=int)
    all_posts = db.session.query(Posts.post_time, Posts.title, Posts.content, Users.username).join(Posts)\
        .order_by(Posts.post_time.desc()).paginate(page=page, per_page=3)
    session.permanent = True
    
    if "username" not in session:
        logging.info('Unknow user connected')
        return render_template('index.html', status="disabled", posts=all_posts)
    else:
        username = session["username"]
        logging.info('User {} connected'.format(username))
        flash("You are already logged in as %s" % username)
        return render_template('index.html', posts=all_posts)
    

@app.route('/search', methods=['GET', 'POST'])
async def search():
    if request.method == "POST":
        username = request.form.get("username")
        if await db.session.query(Users.id).filter_by(username = username).scalar():
            user_id = await db.session.query(Users.id).filter_by(username = username).scalar()
            user_posts = await db.session.query(Posts).filter_by(parent_id=user_id)\
                .order_by(Posts.post_time.desc())
            return render_template('search.html', posts=user_posts, usr=username)
        else:
            logging.info('Post not found by user - {}'.format(username))
            flash("There is no post by  %s" % username)
            return redirect(url_for('index'))
    
  
    
@app.route('/register', methods= ["POST", "GET"])
async def register():
    if "username" in session:
            username = session["username"]
            flash("You are already logged in as %s" % username)
            logging.info('User - {} - already logged'.format(username))
            return render_template("register.html")
    else:
        if request.method == "POST":
            email = request.form.get("email")
            username = request.form.get("username")
            password = request.form.get("password")
            hashed = sha256_crypt.encrypt(password)
            if email == '' or username == '' or password == '':
                flash("Please enter all input fields!")
                return redirect(url_for("register", status="disabled"))
            if await db.session.query(Users.id).filter_by(email = email).scalar() or await db.session.query(Users.id).filter_by(username = username).scalar() is not None:
                flash("The email or username already is being used please choose a different one or login if your an existing user")
                return redirect(url_for("register", status="disabled"))
            register_user = Users(email = email, username = username, password = hashed)
            await db.session.add(register_user)
            await db.session.commit()
            session["username"] = username
            flash("You have logged in as %s" % username)
            logging.info('Register user - {}'.format(username))
            return redirect(url_for('members', usr=username))
        return render_template('register.html', status="disabled")


@app.route('/login', methods= ["POST", "GET"])
async def login():
    if "username" in session:
        username = session["username"]
        flash("You are already logged in as %s" % username)
        logging.info('User - {} - already logged'.format(username))
        return render_template("login.html")
    else:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            hashed = sha256_crypt.encrypt(password)
            if username == '' or password == '':
                flash("Please enter all input fields!")
                return redirect(url_for("login", status="disabled"))
            if await db.session.query(Users.id).filter_by(username = username).scalar():
                if await db.session.query(Users.id).filter_by(password = hashed):
                    await db.session.query(Users.id)
                    session["username"] = username
                    login_user(Users.query.filter_by(username=username).first())
                    flash("You have logged in as %s" % username)
                    return redirect(url_for('members'))
                flash("Password is incorect please try again")
                return redirect(url_for("login", status="disabled"))
            flash("Username or password is incorect please try again or register!")
            logging.info('Login user - {}'.format(username))
            return redirect(url_for("login", status="disabled"))
        
        return render_template('login.html', status="disabled")

@app.route('/my-profile', methods= ["POST", "GET"])
async def my_profile():
    user = Users.query.get(current_user.id)

    if request.method == "POST":
        return render_template('my_profile.html', user=user)
    else:
        username = request.form.get("username")
        if Users.query.filter_by(username=username).first():
            return render_template('my_profile.html', message='Username already exists', user=user)
        
        if not username is None and len(username) > 2 and len(username) < 16:
            user.username = username
            await db.session.commit()
            return redirect(url_for('my_profile'))
        return render_template('my_profile.html', message='Invalid username', user=user)



@app.route('/user/', methods= ["POST", "GET"])
async def members():
    if "username" in session:
        username = session["username"]
        page = request.args.get('page', 1, type=int)
        
        user_id = await db.session.query(Users.id).filter_by(username = username).scalar()
        user_posts = await db.session.query(Posts).filter_by(parent_id=user_id)\
            .order_by(Posts.post_time.desc()).paginate(page=page, per_page=3)
        form = PostForm()
        title = form['title'].data
        content = form['content'].data

        if request.method == "POST":
            post = Posts(post_time=form.post_time ,title=title, content=content, parent_id=user_id)
            await db.session.add(post)
            await db.session.commit()
            flash("Your post was sucesfully submited")
            return redirect(url_for('members', form=form, posts=user_posts))
        return render_template('members.html', form=form, posts=user_posts)
    else:
        return redirect(url_for("index.html", status="disabled"))


@app.route('/edit_post/<string:id>', methods= ["POST", "GET"])
async def edit_post(id):
    post = await db.session.query(Posts).filter_by(id = id).first()
    post_id = await db.session.query(Posts.id).filter_by(id = id).first()
    form = PostForm(obj=post)
    if request.method == "POST":
        form.populate_obj(post)
        await db.session.add(post)
        await db.session.commit()
        flash("The post has been updatet")
        logging.info('The post - {} - has been updatet'.format(post))
        return redirect(url_for('members'))
    return render_template('edit_post.html',id=post_id, form=form)


@app.route('/delete_post/<string:id>', methods=['POST'])
async def delete_post(id):
    if "username" in session:
        await db.session.query(Posts).filter_by(id = id).delete()
        await db.session.commit()

        flash("Post deleted")
        logging.info('Delete post')
        return redirect(url_for('members'))
    else:
        flash("You have to login as a user of the post!")
        return redirect(url_for("login.html", status="disabled"))



@app.route('/logout', methods=["GET"])
def logout():
    if "username" in session:
        session.pop("username", None)
        flash("You have been logged out!")
        logging.info('User - {} - successfully logged out'.format("username"))
        resp = app.make_response(render_template('login.html', status="disabled"))
        resp.set_cookie('token', expires=0)
        return resp 
    else:
        flash("You have been already logged out")
        return redirect(url_for("login.html"))