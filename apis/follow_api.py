from random import randint
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from sqlalchemy import and_, or_
from datetime import datetime

from scripts.err import ERR_WRONG_FORMAT
from scripts.init import MEME_FOLDER, app
from scripts.models import Bookmark, Follow, Like, Meme, MemeTag, Tag, User, Warehouse, db
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
        return respond(1100101, "用户不存在")
    
    if user_id == str(current_user.user_id):
        return respond(1100102, "不能关注自己")
    
    follow = Follow.query.filter(and_(Follow.follower_id==current_user.user_id, Follow.followee_id==user_id)).first()
    if follow is not None:
        return respond(1100103, "无法重复关注")
    
    follow = Follow(
        followee_id=user_id,
        follower_id=current_user.user_id,
    )
    db.session.add(follow)

    db.session.commit()

    return respond(0, "关注成功", {"followId": follow.follow_id})

@app.route("/api/follow-revoke", methods=['POST'])
@login_required
def follow_revoke():
    user_id = request.form.get('userId') or None

    for r in check_null_params(关注用户id=user_id):
        return r
    
    follow = Follow.query.filter(Follow.followee_id==user_id).first()

    if follow is None:
        return respond(1100104, "未关注用户无法取消关注")
    
    
    db.session.delete(follow)

    db.session.commit()

    return respond(0, "取消关注成功")