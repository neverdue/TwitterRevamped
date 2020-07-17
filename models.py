import datetime

from sqlalchemy import desc
from sqlalchemy import or_
from flask_bcrypt import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from peewee import *

db = SQLAlchemy()

class User(UserMixin, db.Model):

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.datetime.now)
    posts = db.relationship('Post', backref="user", lazy=True)
    # is_admin = db.Column(db.Boolean, default=False)


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def get_posts(self):
        # return Post.select().where(Post.user == self)
        # db.session.close()
        return Post.query.filter(Post.user == self).order_by(Post.timestamp.desc()).all()

    def get_stream(self):
        # store = OrderedSet()
        # return Post.select().where(
        #     (Post.user << self.following()) |
        #     (Post.user == self)
        # )
        # print(self)
        # print(self.following()[0][0])
        list = [user[0] for user in self.following()]
        if len(list) == 0:
            return []
        # print(list)
        # for user in list:
        #     print(f'get stream waala {user.id}')
        #     result = Post.query.filter((Post.user == user)).order_by(Post.id).all()
        #     store.update(result)
        cond = or_(*[Post.user == user for user in list])
        result = Post.query.filter(cond).order_by(Post.timestamp.desc()).all()
        # store.update(result)
        # print(store)
        # db.session.close()
        return result

    def following(self):
        """The users that we are following."""
        list = []
        # return (
        #     User.select().join(
        #         Relationship, on=Relationship.to_user
        #     ).where(
        #         Relationship.from_user == self
        #     )
        # )
        # return (User.query.filter(Relationship.from_user == self).all())
        # return db.session.query(Relationship).select_from(User).join(Relationship.to_user_id).filter(Relationship.from_user_id == self.id).first()
        print(self.id)
        # result = db.session.execute("select (users.id, username, email, password, joined_at) from users inner join relationship on (relationship.to_user_id = users.id) where (relationship.from_user_id = :self)", {"self": self.id})
        result = db.session.query(User, Relationship).filter(Relationship.to_user_id == User.id).filter(Relationship.from_user_id == self.id).all()
        # db.session.close()
        return result

    def followingStream(self):
        """The users that we are following."""
        list = []
        # return (
        #     User.select().join(
        #         Relationship, on=Relationship.to_user
        #     ).where(
        #         Relationship.from_user == self
        #     )
        # )
        # return (User.query.filter(Relationship.from_user == self).all())
        # return db.session.query(Relationship).select_from(User).join(Relationship.to_user_id).filter(Relationship.from_user_id == self.id).first()
        print(self.id)
        # result = db.session.execute("select (users.id, username, email, password, joined_at) from users inner join relationship on (relationship.to_user_id = users.id) where (relationship.from_user_id = :self)", {"self": self.id})
        result = db.session.query(User, Relationship).filter(Relationship.to_user_id == User.id).filter(Relationship.from_user_id == self.id).all()
        # db.session.close()
        list = [user for user, relationship in result]
        return list


    def followers(self):
        """Get users following the current user"""
        list = []
        # return (
        #     User.select().join(
        #         Relationship, on=Relationship.from_user
        #     ).where(
        #         Relationship.to_user == self
        #     )
        # )
            # User.query.filter(Relationship.to_user == self).all()
        # return db.session.execute("select * from users as t1 inner join relationship as t2 on (:t2.from_user_id = t1.id) where (:t2.to_user_id = :self.id)", {"t2.from_user_id":2, "t2.to_user_id": 1, "self.id": self.id})
        # User.select().join(Relationship, on=Relationship.from_user).where(Relationship.to_user == self)
        # return (User.query.filter(Relationship.from_user == self).all())
        print(self.id)
        # result = db.session.execute("select (users.id, username, email, password, joined_at) from users inner join relationship on (relationship.from_user_id = users.id) where (relationship.to_user_id = :self)", {"self": self.id})
        result = db.session.query(User, Relationship).filter(Relationship.from_user_id == User.id).filter(Relationship.to_user_id == self.id).all()
        # db.session.close()
        return result


    # @classmethod
    # def create_user(cls, username, email, password, admin=False):
    #     try:
    #         with DATABASE.transaction():
    #             cls.create(
    #                 username=username,
    #                 email=email,
    #                 password=generate_password_hash(password),
    #                 is_admin=admin)
    #     except IntegrityError:
    #         raise ValueError("User already exists")


class Post(db.Model):

    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content

    # db.session.close()

    class Meta:
        database = db
        order_by = ('-timestamp',)


class Relationship(db.Model):

    __tablename__ = 'relationship'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    from_user = db.relationship("User", foreign_keys=[from_user_id], lazy=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    to_user = db.relationship("User", foreign_keys=[to_user_id], lazy=True)
    # db.session.close()
    class Meta:
        database = db
        indexes = (
            ((('from_user', 'to_user'), True),)
        )

#
# def initialize():
#     DATABASE.connect()
#     DATABASE.create_tables([User, Post, Relationship], safe=True)
#     DATABASE.close()
