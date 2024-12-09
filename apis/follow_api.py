from random import randint
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from sqlalchemy import and_, or_
from datetime import datetime

from scripts.err import ERR_FOLLOW_EXISTS, ERR_FOLLOW_NOT_FOUND, ERR_SELF_FOLLOW, ERR_USER_NOT_FOUND, ERR_WRONG_FORMAT
from scripts.init import MEME_FOLDER, app
from scripts.models import Bookmark, Follow, Like, Meme, MemeTag, Message, Tag, User, Warehouse, db
from scripts.utils import allowed_file, check_null_params, respond


follow_api = Blueprint('follow_api', __name__, template_folder='../templates')
current_user:User

@app.route("/api/follow-add", methods=['POST'])
@login_required
def follow_add():
    user_id = request.form.get('userId') or None

    for r in check_null_params(用户id=user_id):
        return r
    
    user = User.query.filter(User.user_id==user_id).first()

    if user is None:
        return respond(ERR_USER_NOT_FOUND, "用户不存在")
    
    if user_id == str(current_user.user_id):
        return respond(ERR_SELF_FOLLOW, "不能关注自己")
    
    follow = Follow.query.filter(and_(Follow.follower_id==current_user.user_id, Follow.followee_id==user_id)).first()
    if follow is not None:
        return respond(ERR_FOLLOW_EXISTS, "无法重复关注")
    
    follow = Follow(
        followee_id=user_id,
        follower_id=current_user.user_id,
    )
    db.session.add(follow)
    follow_message = Message(
        user_id = follow.followee_id,
        id_type = "User",
        content = f"{current_user.username}关注了您",
        with_id = current_user.user_id
    )
    db.session.add(follow_message)

    db.session.commit()

    return respond(0, "关注成功", {"followId": follow.follow_id})

@app.route("/api/follow-check", methods=['POST'])
@login_required
def follow_check():
    user_id = request.form.get('userId')

    for r in check_null_params(用户id=user_id):
        return r
    
    user = User.query.filter(User.user_id==user_id).first()

    if user is None:
        return respond(ERR_USER_NOT_FOUND, "用户不存在")

    if user_id == str(current_user.user_id):
        return respond(0, "查询成功", {"isfollowing": False})

    follow = Follow.query.filter(and_(Follow.follower_id==current_user.user_id, Follow.followee_id==user_id)).first()
    if follow is not None:
        return respond(0, "查询成功", {"isfollowing":True})
    else:
        return respond(0, "查询成功", {"isfollowing":False})

@app.route("/api/follow-revoke", methods=['POST'])
@login_required
def follow_revoke():
    user_id = request.form.get('userId') or None

    for r in check_null_params(关注用户id=user_id):
        return r
    
    follow = Follow.query.filter(Follow.followee_id==user_id).first()

    if follow is None:
        return respond(ERR_FOLLOW_NOT_FOUND, "未关注用户无法取消关注")
    
    
    db.session.delete(follow)

    db.session.commit()

    return respond(0, "取消关注成功")

@app.route("/api/follow-get-followee-num", methods=["POST"])
@login_required
def follow_get_followee_num():
    user = current_user

    if user is None:
        return respond(ERR_USER_NOT_FOUND, "用户不存在")
    
    user_id = user.get_id()
    
    followee_num = Follow.query.filter(Follow.followee_id==user_id).count()

    return respond(0, "查询成功", {"followeeNum": followee_num})

@app.route("/api/follow-get-follower-num", methods=["POST"])
@login_required
def follow_get_follower_num():
    user = current_user
    
    if user is None:
        return respond(ERR_USER_NOT_FOUND, "用户不存在")
    
    user_id = user.get_id()
    
    follower_num = Follow.qure.filter(Follow.follower_id==user_id).count()
    
    return respond(0, "查询成功", {"followerNum": follower_num})

@app.route("/api/follow-get-followees", methods=["POST"])
@login_required
def follow_get_followees():
    user = current_user
    
    if user is None:
        return respond(ERR_USER_NOT_FOUND, "用户不存在")
    
    user_id = user.get_id()
    
    followees = db.session.query(
        User.user_id,
        User.profile_picture
    ).join(
        Follow, 
        User.user_id == Follow.followee_id
    ).filter(
        Follow.follower_id == user_id
    ).all()
    
    result = [
        {
            "user_id": user_id,
            "profile_picture": profile_picture or ""  # 处理None值
        }
        for user_id, profile_picture in followees
    ]
    
    return respond(0, "查询成功", {"followees": result})
    
    
    
@app.route("/api/follow-get-followers", methods=["POST"])
@login_required
def follow_get_followers():
    user = current_user
    
    if user is None :
        return respond(ERR_USER_NOT_FOUND, "用户不存在")
    
    user_id = user.get_id()
    
    followers = db.session.query(
        User.user_id,
        User.profile_picture
    ).join(
        Follow,
        User.user_id == Follow.follower_id
    ).filter(
        Follow.followee_id == user_id
    ).all()
    
    result = [
        {
            "user_id": user_id,
            "profile_picture": profile_picture or ""  # 处理None值
        }
        for user_id, profile_picture in followers
    ]
    
    return respond(0, "查询成功", {"followers": result})
    
    