from website.models import Users, Posts, PostForm
from website import create_app
from flask import render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
from website import db
from flask_login import login_user
from flask_toastr import Toastr
import logging

#logging.basicConfig(filename='app.log', level=logging.INFO,
#                    format='%(levelname)s:%(message)s')

app = create_app("config.MyConfig")

toastr = Toastr(app)

@app.route('/')
def index():
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
def search():
    if request.method == "POST":
        username = request.form.get("username")
        if db.session.query(Users.id).filter_by(username = username).scalar():
            user_id = db.session.query(Users.id).filter_by(username = username).scalar()
            user_posts = db.session.query(Posts).filter_by(user_id=user_id)\
                .order_by(Posts.post_time.desc())
            return render_template('search.html', posts=user_posts, usr=username)
        else:
            logging.info('Post not found by user - {}'.format(username))
            flash("There is no post by  %s" % username)
            return redirect(url_for('index'))



@app.route('/register', methods= ["POST", "GET"])
def register():
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
            if db.session.query(Users.id).filter_by(email = email).scalar() or db.session.query(Users.id).filter_by(username = username).scalar() is not None:
                flash("The email or username already is being used please choose a different one or login if your an existing user")
                return redirect(url_for("register", status="disabled"))
            register_user = Users(email = email, username = username, password = hashed)
            db.session.add(register_user)
            db.session.commit()
            session["username"] = username
            flash("You have logged in as %s" % username)
            logging.info('Register user - {}'.format(username))
            return redirect(url_for('members', usr=username))
        return render_template('register.html', status="disabled")


@app.route('/login', methods= ["POST", "GET"])
def login():
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
            if db.session.query(Users.id).filter_by(username = username).first():
                if db.session.query(Users.id).filter_by(password = hashed):
                    db.session.query(Users.id)
                    session["username"] = username
                    db_user = Users.query.filter_by(username=username).first()
                    login_user(db_user)
                    flash("You have logged in as %s" % username)
                    return redirect(url_for('members'))
                flash("Password is incorect please try again")
                return redirect(url_for("login", status="disabled"))
            flash("Username or password is incorect please try again or register!")
            logging.info('Login user - {}'.format(username))
            return redirect(url_for("login", status="disabled"))

        return render_template('login.html', status="disabled")

@app.route('/user/', methods= ["POST", "GET"])
def members():
    if "username" in session:
        username = session["username"]
        page = request.args.get('page', 1, type=int)

        user_id = db.session.query(Users.id).filter_by(username = username).scalar()
        user_posts = db.session.query(Posts).filter_by(user_id=user_id)\
            .order_by(Posts.post_time.desc()).paginate(page=page, per_page=3)
        form = PostForm()
        title = form['title'].data
        content = form['content'].data

        if request.method == "POST":
            post = Posts(post_time=form.post_time ,title=title, content=content, user_id=user_id)
            db.session.add(post)
            db.session.commit()
            flash("Your post was sucesfully submited")
            return redirect(url_for('members', form=form, posts=user_posts))
        return render_template('members.html', form=form, posts=user_posts)
    else:
        return redirect(url_for("index.html", status="disabled"))


@app.route('/edit_post/<string:id>', methods= ["POST", "GET"])
def edit_post(id):
    post = db.session.query(Posts).filter_by(id = id).first()
    post_id = db.session.query(Posts.id).filter_by(id = id).first()
    form = PostForm(obj=post)
    if request.method == "POST":
        form.populate_obj(post)
        db.session.add(post)
        db.session.commit()
        flash("The post has been updatet")
        logging.info('The post - {} - has been updatet'.format(post))
        return redirect(url_for('members'))
    return render_template('edit_post.html',id=post_id, form=form)


@app.route('/delete_post/<string:id>', methods=['POST'])
def delete_post(id):
    if "username" in session:
        db.session.query(Posts).filter_by(id = id).delete()
        db.session.commit()

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
