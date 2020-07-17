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
    # is_admin = Column(Boolean, default=False)


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.name)

    def get_posts(self):
        # return Post.select().where(Post.user == self)
        # session.close()
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
        # session.close()
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
        # return session.query(Relationship).select_from(User).join(Relationship.to_user_id).filter(Relationship.from_user_id == self.id).first()
        print(self.id)
        # result = session.execute("select (users.id, username, email, password, joined_at) from users inner join relationship on (relationship.to_user_id = users.id) where (relationship.from_user_id = :self)", {"self": self.id})
        result = db_session.query(User, Relationship).filter(Relationship.to_user_id == User.id).filter(Relationship.from_user_id == self.id).all()
        # session.close()
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
        # return session.query(Relationship).select_from(User).join(Relationship.to_user_id).filter(Relationship.from_user_id == self.id).first()
        print(self.id)
        # result = session.execute("select (users.id, username, email, password, joined_at) from users inner join relationship on (relationship.to_user_id = users.id) where (relationship.from_user_id = :self)", {"self": self.id})
        result = db_session.query(User, Relationship).filter(Relationship.to_user_id == User.id).filter(Relationship.from_user_id == self.id).all()
        # session.close()
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
        # return session.execute("select * from users as t1 inner join relationship as t2 on (:t2.from_user_id = t1.id) where (:t2.to_user_id = :self.id)", {"t2.from_user_id":2, "t2.to_user_id": 1, "self.id": self.id})
        # User.select().join(Relationship, on=Relationship.from_user).where(Relationship.to_user == self)
        # return (User.query.filter(Relationship.from_user == self).all())
        print(self.id)
        # result = session.execute("select (users.id, username, email, password, joined_at) from users inner join relationship on (relationship.from_user_id = users.id) where (relationship.to_user_id = :self)", {"self": self.id})
        result = db_session.query(User, Relationship).filter(Relationship.from_user_id == User.id).filter(Relationship.to_user_id == self.id).all()
        # session.close()
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


class Post(Base):

    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content

    # session.close()

    # class Meta:
    #     database = db
    #     order_by = ('-timestamp',)


class Relationship(Base):

    __tablename__ = 'relationship'
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_user = relationship("User", foreign_keys=[from_user_id], lazy=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user = relationship("User", foreign_keys=[to_user_id], lazy=True)
    # session.close()
    # class Meta:
    #     database = db
    #     indexes = (
    #         ((('from_user', 'to_user'), True),)
    #     )

#
# def initialize():
#     DATABASE.connect()
#     DATABASE.create_tables([User, Post, Relationship], safe=True)
#     DATABASE.close()
