from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Column, Integer, String, Text, ForeignKey, Date, DateTime
from scripts.init import app

db: SQLAlchemy = SQLAlchemy(app)

# TODO: define entities and relations here


# Entities
class User(db.Model):
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(256), unique=True, nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    profile_picture = Column(String(256), nullable=True)
    bio = Column(Date, nullable=False)
    signup_data = Column(Integer, nullable=False)
    hugo_coin = Column(Integer, nullable=False)


class Meme(db.Model):
    meme_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(256), nullable=False)
    upload_time = Column(DateTime, nullable=False)
    views = Column(Integer, nullable=False, default=0)
    likes = Column(Integer, nullable=False, default=0)


class Tag(db.Model):
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), unique=True, nullable=False)


class Warehouse(db.Model):
    warehouse_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    capacity = Column(Integer, nullable=False)


class Post(db.Model):
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    post_time = Column(DateTime, nullable=False)


class Comment(db.Model):
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id"), nullable=False)
    to_comment_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    comment_time = Column(DateTime, nullable=False)


# Relations
class Follow(db.Model):
    follow_id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    followee_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)


class Like(db.Model):
    like_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    like_date = Column(DateTime, nullable=False)


class Bookmark(db.Model):
    bookmark_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    bookmark_date = Column(DateTime, nullable=False)


class Report(db.Model):
    report_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    reason = Column(Text, nullable=False)
    report_date = Column(DateTime, nullable=False)
    status = Column(String(256), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'resolved')", name="check_status"),
    )


class MemeTag(db.Model):
    memetag_id = Column(Integer, primary_key=True, autoincrement=True)
    meme_id = Column(Integer, ForeignKey("meme.meme_id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tag.tag_id"), nullable=False)


# Initialize the database
with app.app_context():
    db.create_all()
    # drop_all()
