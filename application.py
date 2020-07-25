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
from create import db_session, init_db

import forms
import models

init_db()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.query.get(int(userid))
    except models.DoesNotExist:
        return None


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        username=form.username.data
        email=form.email.data
        hashed_pswd=generate_password_hash(form.password.data).decode('utf8')
        user = models.User(username=username, email=email, password=hashed_pswd)
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.query.filter_by(email=form.email.data).first()
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        user = current_user.id
        post = models.Post(user_id=user, content=form.content.data.strip())
        flash("Message posted! Thanks!", "success")
        db_session.add(post)
        db_session.commit()
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/')
def index():
    stream = models.Post.query.order_by(models.Post.id.desc()).limit(100).all()
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if current_user.is_authenticated:
        if username:
            try:
                user = models.User.query.filter(models.User.username.like(username)).first()
            except models.DoesNotExist:
                abort(404)
            else:
                stream = user.get_posts()
        if username:
            template = 'user_stream.html'
    else:
        flash("Login before accessing this page", "error")
        abort(404)
    return render_template(template, stream=stream, user=user)

@app.route('/stream/following')
def streamFollowing():
    template = 'user_stream.html'
    if current_user.is_authenticated:
        stream = current_user.get_stream()
        user = current_user
    else:
        flash("Login before accessing this page", "error")
        abort(404)
    return render_template(template, stream=stream, user=user)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.query.filter(models.Post.id == post_id).all()
    if len(posts) == 0:
        abort(404)
    return render_template('stream.html', stream=posts)

@app.route('/post/delete/<int:post_id>')
def delete_post(post_id):
    posts = models.Post.query.filter(models.Post.id == post_id).first()
    if (posts):
        db_session.delete(posts)
        db_session.commit()
        flash("You've successfully deleted the post!", "success")
        return redirect(url_for('index'))
    else:
        abort(404)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.query.filter(models.User.username.like(username)).first()
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            relationship = models.Relationship(from_user_id=current_user.id, to_user_id=to_user.id)
            db_session.add(relationship)
            db_session.commit()
        except models.IntegrityError:
            pass
        else:
            flash("You're now following {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.query.filter(models.User.username.like(username)).first()
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            relationship = db_session.query(models.Relationship).filter(and_((models.Relationship.from_user_id==current_user.id), (models.Relationship.to_user_id==to_user.id))).first()
            db_session.delete(relationship)
            db_session.commit()
        except models.IntegrityError:
            pass
        else:
            flash("You've unfollowed {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
