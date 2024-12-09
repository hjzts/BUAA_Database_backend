from random import randint
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from sqlalchemy import and_, or_
from datetime import datetime

from scripts.err import ERR_LIKE_EXISTS, ERR_LIKE_NOT_FOUND, ERR_MEME_NOT_FOUND, ERR_WRONG_FORMAT
from scripts.init import MEME_FOLDER, app
from scripts.models import Bookmark, Like, Meme, MemeTag, Tag, User, Warehouse, db
from scripts.utils import allowed_file, check_null_params, respond


like_api = Blueprint('like_api', __name__, template_folder='../templates')
current_user:User

@app.route("/api/like-add", methods=['POST'])
@login_required
def like_add():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r
    
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")
    
    like = Like.query.filter(and_(Like.user_id==current_user.user_id, Like.meme_id==meme_id)).first()
    if like is not None:
        return respond(ERR_LIKE_EXISTS, "已点赞")
    
    like = Like(
        meme_id=meme_id,
        user_id=current_user.user_id,
    )
    db.session.add(like)

    meme.likes += 1

    db.session.commit()

    return respond(0, "点赞成功", {"likeId": like.like_id})

@app.route("/api/like-check", methods=['POST'])
@login_required
def like_check():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")
    
    like = Like.query.filter(and_(Like.user_id==current_user.user_id, Like.meme_id==meme_id)).first()
    if like is not None:
        return respond(0, "查询成功", {"liked": True})
    else:
        return respond(0, "查询成功", {"liked": False})

@app.route("/api/like-revoke", methods=['POST'])
@login_required
def like_revoke():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r
    
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")
    
    like = Like.query.filter(and_(Like.user_id==current_user.user_id, Like.meme_id==meme_id)).first()
    if like is None:
        return respond(ERR_LIKE_NOT_FOUND, "点赞不存在")
    
    Like.query.filter(and_(Like.user_id==current_user.user_id, Like.meme_id==meme_id)).delete()
    meme.likes -= 1

    db.session.commit()

    return respond(0, "取消成功")

@app.route("/api/like-get-num",methods=["POST"])
@login_required
def like_get_num():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r

    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")
    
    return respond(0, "查询成功", {"likes": meme.likes})