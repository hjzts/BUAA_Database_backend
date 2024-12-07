from email import message
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from scripts.init import app

db: SQLAlchemy = SQLAlchemy(app)

# Entities
class User(db.Model, UserMixin):
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(256), unique=True, nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    profile_picture = Column(String(256), nullable=True)
    bio = Column(Text, nullable=True)
    signup_time = Column(DateTime, nullable=False, default=datetime.now())
    hugo_coin = Column(Integer, nullable=False, default=0)
    is_ban = Column(Boolean, nullable=False, default=False)

    def get_id(self):
        return self.user_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Meme(db.Model):
    meme_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    caption = Column(Text, nullable=True)
    image_url = Column(String(256), nullable=False)
    upload_time = Column(DateTime, nullable=False, default=datetime.now())
    views = Column(Integer, nullable=False, default=0)
    likes = Column(Integer, nullable=False, default=0)
    is_block = Column(Boolean, nullable=False, default=False)

    ref_memetags = db.relationship('MemeTag', backref='meme', cascade='all, delete-orphan')
    ref_comments = db.relationship('Comment', backref='meme', cascade='all, delete-orphan')
    ref_likes = db.relationship('Like', backref='meme', cascade='all, delete-orphan')
    ref_bookmarks = db.relationship('Bookmark', backref='meme', cascade='all, delete-orphan')
    ref_reports = db.relationship('Report', backref='meme', cascade='all, delete-orphan')


class Tag(db.Model):
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), unique=True, nullable=False)


class Warehouse(db.Model):
    warehouse_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    name = Column(String(256), nullable=False)
    capacity = Column(Integer, nullable=False, default=30) # 剩余容量

    ref_bookmarks = db.relationship('Bookmark', backref='warehouse', cascade='all, delete-orphan')


class Post(db.Model):
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    bounty = Column(Integer, nullable=False)
    post_time = Column(DateTime, nullable=False, default=datetime.now())

    ref_postbounties = db.relationship('PostBounty', backref='post', cascade='all, delete-orphan')
    

class Comment(db.Model):
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id", ondelete='CASCADE'), nullable=False)
    to_comment_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    comment_time = Column(DateTime, nullable=False, default=datetime.now())

class Message(db.Model):
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    idType = Column(String, nullable=False, default="normal") # normal | withId
    content = Column(String, nullable=False)
    with_id = Column(Integer, nullable=True) # meme_id, comment_id
    read = Column(Boolean, nullable=False, default=False)
    message_time = Column(DateTime, nullable=False, default=datetime.now())


# Relations
class Follow(db.Model):
    follow_id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    followee_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)


class Like(db.Model):
    like_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id", ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    like_date = Column(DateTime, nullable=False, default=datetime.now())


class Bookmark(db.Model):
    bookmark_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id", ondelete='CASCADE'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouse.warehouse_id", ondelete='CASCADE'), nullable=False)
    bookmark_time = Column(DateTime, nullable=False, default=datetime.now())


class Report(db.Model):
    report_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id", ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=True) # could be anonymous
    reason = Column(Text, nullable=False)
    report_time = Column(DateTime, nullable=False, default=datetime.now())
    status = Column(String(256), nullable=False, default='pending')

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'resolved')", name="check_status"),
    )


class MemeTag(db.Model):
    memetag_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id", ondelete='CASCADE'), nullable=False)
    tag_id = Column(Integer, ForeignKey("tag.tag_id"), nullable=False)


class PostBounty(db.Model):
    postbounty_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("post.post_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    bounty = Column(Integer, nullable=False)

    

# Initialize the database
with app.app_context():
    db.create_all()

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    return user
    
