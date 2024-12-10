from random import randint
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from sqlalchemy import and_, or_
from datetime import datetime

from scripts.err import ERR_BALANCE_INSUFFICIENT, ERR_POST_NOT_FOUND, ERR_WRONG_FORMAT
from scripts.init import MEME_FOLDER, app
from scripts.models import Bookmark, Comment, Like, Meme, MemeTag, Post, PostBounty, Tag, User, Warehouse, db
from scripts.utils import allowed_file, check_null_params, respond


post_api = Blueprint('post_api', __name__, template_folder='../templates')
current_user:User

DEFAULT_BOUNTY="5"

@app.route("/api/post-create", methods=['POST'])
@login_required
def post_create():
    content = request.form.get('content') or None
    bounty = request.form.get('bounty') or DEFAULT_BOUNTY

    for r in check_null_params(请求贴内容=content):
        return r
    
    if not bounty.isdecimal():
        return respond(ERR_WRONG_FORMAT, "悬赏金额需为正整数")
    
    print(int(current_user.hugo_coin),int(bounty))
    if int(current_user.hugo_coin) < int(bounty):
        return respond(ERR_BALANCE_INSUFFICIENT, f"用户余额不足{int(bounty)}，无法添加悬赏金额")
    
    post = Post(
        user_id=current_user.user_id,
        content=content,
        bounty=bounty
    )
    db.session.add(post)
    db.session.commit()

    postBounty = PostBounty(
        post_id=post.post_id,
        user_id=current_user.user_id,
        bounty=bounty
    )
    db.session.add(postBounty)

    current_user.hugo_coin -= int(bounty)

    db.session.commit()

    return respond(0, "发布成功", {"postId": post.post_id})

@app.route("/api/post-delete", methods=['POST'])
@login_required
def post_delete():
    post_id = request.form.get('postId') or None

    for r in check_null_params(请求贴id=post_id):
        return r
    
    post = Post.query.filter(and_(Post.user_id==current_user.user_id, Post.post_id==post_id)).first()

    if post is None:
        return respond(ERR_POST_NOT_FOUND, "请求贴不存在或无权操作")

    # bounty refund
    for postBounty in PostBounty.query.filter(PostBounty.post_id==post_id).all():
        user:User = User.query.filter(User.user_id==postBounty.user_id)
        user.hugo_coin += postBounty.bounty
    
    db.session.delete(post) # recurrently delete all sub-comments

    db.session.commit()

    return respond(0, "删除成功")

@app.route("/api/post-get", methods=['POST'])
@login_required
def post_get():
    posts_data = {
        "posts": [{
            "postId": post.post_id,
            "username": User.query.filter(User.user_id==post.user_id).first().username,
            "user_profile_picture":User.query.filter(User.user_id==post.user_id).first().profile_picture,
            "content": post.content,
            "bounty": post.bounty,
            "postTime": post.post_time
        } for post in Post.query.all()]
    }

    return respond(0, "获取成功", posts_data)

@app.route("/api/post-get-num-all", methods=["POST"])
@login_required
def post_get_num_all():
    post_num = len(Post.query.all())

    return respond(0, "获取成功", {"postNum": post_num})

@app.route("/api/post-get-num", methods=["POST"])
@login_required
def post_get_num():
    posts = Post.query.filter(Post.user_id==current_user.user_id).all()
    
    post_num = 0 if posts is None else len(posts)

    return respond(0, "获取成功", {"postNum": post_num})

@app.route("/api/post-add-bounty", methods=['POST'])
@login_required
def post_add_bounty():

    post_id = request.form.get('postId') or None
    bounty = request.form.get('bounty') or DEFAULT_BOUNTY

    for r in check_null_params(请求贴id=post_id):
        return r
    
    post = Post.query.filter(Post.post_id==post_id).first()

    if post is None:
        return respond(ERR_POST_NOT_FOUND, "请求贴不存在")
    
    if not bounty.isdecimal():
        return respond(ERR_WRONG_FORMAT, "悬赏金额需为正整数")
    
    if int(current_user.hugo_coin) < int(bounty):
        return respond(ERR_BALANCE_INSUFFICIENT, f"用户余额不足{int(bounty)}，无法添加悬赏金额")

    post.bounty += int(bounty)
    current_user.hugo_coin -= int(bounty)
    
    postBounty = PostBounty(
        post_id=post_id,
        user_id=current_user.user_id,
        bounty=int(bounty)
    )
    
    db.session.add(postBounty)

    db.session.commit()

    return respond(0, "添加成功")