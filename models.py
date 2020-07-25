import datetime

from sqlalchemy import desc
from sqlalchemy import or_
from flask_bcrypt import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from create import Base, db_session
from sqlalchemy.orm import sessionmaker, relationship


class User(UserMixin, Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    email = Column(String(), unique=True, nullable=False)
    password = Column(String(), nullable=False)
    joined_at = Column(DateTime, default=datetime.datetime.now)
    posts = relationship('Post', backref="user", lazy=True)


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.name)

    def get_posts(self):
        return Post.query.filter(Post.user == self).order_by(Post.timestamp.desc()).all()

    def get_stream(self):
        list = [user[0] for user in self.following()]
        if len(list) == 0:
            return []
        cond = or_(*[Post.user == user for user in list])
        result = Post.query.filter(cond).order_by(Post.timestamp.desc()).all()
        return result

    def following(self):
        """The users that we are following."""
        result = db_session.query(User, Relationship).filter(Relationship.to_user_id == User.id).filter(Relationship.from_user_id == self.id).all()
        return result

    def followingStream(self):
        """The users that we are following."""
        list = []
        result = self.following()
        list = [user for user, relationship in result]
        return list


    def followers(self):
        """Get users following the current user"""
        list = []
        result = db_session.query(User, Relationship).filter(Relationship.from_user_id == User.id).filter(Relationship.to_user_id == self.id).all()
        return result


class Post(Base):

    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content

class Relationship(Base):

    __tablename__ = 'relationship'
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_user = relationship("User", foreign_keys=[from_user_id], lazy=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user = relationship("User", foreign_keys=[to_user_id], lazy=True)
