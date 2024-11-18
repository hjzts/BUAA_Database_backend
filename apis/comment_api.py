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
from scripts.models import Bookmark, Comment, Like, Meme, MemeTag, Tag, User, Warehouse, db
from scripts.utils import allowed_file, check_null_params, respond


comment_api = Blueprint('comment_api', __name__, template_folder='../templates')
current_user:User

@app.route("/api/comment-add", methods=['POST'])
@login_required
def comment_add():
    meme_id = request.form.get('memeId') or None
    to_comment_id = request.form.get('toCommentId') or None
    content = request.form.get('content') or None

    for r in check_null_params(表情包id=meme_id, 评论内容=content):
        return r
    
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(800101, "表情包不存在")
    
    if to_comment_id is not None:
        to_comment = Comment.query.filter(Comment.comment_id==to_comment_id).first()
        if to_comment is None:
            return respond(800102, "回复的评论不存在")
    
    comment = Comment(
        meme_id=meme_id,
        to_comment_id=to_comment_id,
        user_id=current_user.user_id,
        content=content
    )
    db.session.add(comment)

    db.session.commit()

    return respond(0, "评论成功", {"CommentId": comment.comment_id})

@app.route("/api/comment-delete", methods=['POST'])
@login_required
def comment_delete():
    comment_id = request.form.get('commentId') or None

    for r in check_null_params(评论id=comment_id):
        return r
    
    comment = Comment.query.filter(and_(Comment.user_id==current_user.user_id, Comment.comment_id==comment_id)).first()

    if comment is None:
        return respond(800103, "评论不存在或无权操作")
    
    def recurrent_delete(top_comment: Comment):
        sub_comments = Comment.query.filter(Comment.to_comment_id==top_comment.comment_id).all()
        for sub_comment in sub_comments:
            recurrent_delete(sub_comment)
        db.session.delete(top_comment)

    recurrent_delete(comment) # recurrently delete all sub-comments

    db.session.commit()

    return respond(0, "删除成功")