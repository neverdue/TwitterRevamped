import os

from flask import (Flask, g, render_template, flash, redirect, url_for,
                  abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
import datetime

from sqlalchemy import desc
from sqlalchemy import or_, and_
from flask_bcrypt import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from peewee import *

import forms
import models



app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET')
app.secret_key = 'dasdsadasdsadas'

# Configure database
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://llcmqqdiourazq:0a7e57b9c9d71aec4dd37d40d688b7b01115237fe7b56840b7cd80e88884cdd9@ec2-52-20-248-222.compute-1.amazonaws.com:5432/d4nteal0mkk14o'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        db.session.close()
        return models.User.query.get(int(userid))
    except models.DoesNotExist:
        db.session.close()
        return None


# @app.before_request
# def before_request():
#     """Connect to the database before each request."""
#     g.db = models.DATABASE
#     g.db.connect()
#     g.user = current_user
#
#
# @app.after_request
# def after_request(response):
#     """Close the database connection after each request."""
#     db.session.close()
#     return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        username=form.username.data
        email=form.email.data
        hashed_pswd=generate_password_hash(form.password.data).decode('utf8')
        user = models.User(username=username, email=email, password=hashed_pswd)
        db.session.add(user)
        db.session.commit()
        db.session.close()
        return redirect(url_for('index'))
    db.session.close()
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            # user = models.User.get(models.User.email == form.email.data)
            user = models.User.query.filter_by(email=form.email.data).first()
            db.session.close()
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    db.session.close()
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    db.session.close()
    return redirect(url_for('index'))


@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        user = current_user.id
        post = models.Post(user_id=user, content=form.content.data.strip())
        # models.Post.create(user=g.user.id,
        #                    content=form.content.data.strip())
        flash("Message posted! Thanks!", "success")
        db.session.add(post)
        db.session.commit()
        db.session.close()
        return redirect(url_for('index'))
    db.session.close()
    return render_template('post.html', form=form)


@app.route('/')
def index():
    stream = models.Post.query.order_by(models.Post.id.desc()).limit(100).all()
    db.session.close()
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:
            # user = models.User.select().where(
            #     models.User.username**username).get()
            user = models.User.query.filter(models.User.username.like(username)).first()
            db.session.close()
        except models.DoesNotExist:
            abort(404)
        else:
            # stream = user.posts.limit(100)
            # user = models.User.query.filter(models.User.username.like(username)).first()
            # stream = models.Post.query.filter(models.Post.user_id == user.id).all()
            stream = user.get_posts()
            db.session.close()
    else:
        # stream = current_user.get_stream().limit(100)
        # user = models.User.query.filter(models.User.username.like(username)).first()
        stream = current_user.get_stream()
        user = current_user
        db.session.close()
        # stream = models.Post.query.filter(models.Post.user_id == user.id).all()
    if username:
        template = 'user_stream.html'
    db.session.close()
    return render_template(template, stream=stream, user=user)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    # posts = models.Post.select().where(models.Post.id == post_id)
    posts = models.Post.query.filter(models.Post.id == post_id).all()
    if len(posts) == 0:
        abort(404)
        db.session.close()
    db.session.close()
    return render_template('stream.html', stream=posts)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        # to_user = models.User.get(models.User.username**username)
        to_user = models.User.query.filter(models.User.username.like(username)).first()
        db.session.close()
    except models.DoesNotExist:
        abort(404)
        db.session.close()
    else:
        try:
            # r = models.Relationship.create(
            #     from_user=current_user,
            #     to_user=to_user
            # )
            relationship = models.Relationship(from_user_id=current_user.id, to_user_id=to_user.id)
            db.session.add(relationship)
            db.session.commit()
            db.session.close()
        except models.IntegrityError:
            pass
        else:
            flash("You're now following {}!".format(to_user.username), "success")
    db.session.close()
    return redirect(url_for('stream', username=to_user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        # to_user = models.User.get(models.User.username**username)
        to_user = models.User.query.filter(models.User.username.like(username)).first()
        db.session.close()
        print(to_user.username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            # models.Relationship.get(
            #     from_user=g.user._get_current_object(),
            #     to_user=to_user
            # )
            relationship = db.session.query(models.Relationship).filter_by(to_user_id=to_user.id).first()
            db.session.delete(relationship)
            db.session.commit()
            db.session.close()
        except models.IntegrityError:
            pass
        else:
            flash("You've unfollowed {}!".format(to_user.username), "success")
    db.session.close()
    return redirect(url_for('stream', username=to_user.username))


@app.errorhandler(404)
def not_found(error):
    db.session.close()
    return render_template('404.html'), 404



if __name__ == '__main__':
    # models.initialize()
    # try:
    #     models.User.create_user(
    #         username='mayankpandey',
    #         email='mp.pandey86@gmail.com',
    #         password='random',
    #         admin=True
    #     )
    # except ValueError:
    #     pass
    app.run(debug=True)
