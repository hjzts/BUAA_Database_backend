from random import randint
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from sqlalchemy import and_, or_
from datetime import datetime

from scripts.err import ERR_COMMENT_NOT_FOUND, ERR_MEME_NOT_FOUND, ERR_WRONG_FORMAT
from scripts.init import MEME_FOLDER, app
from scripts.models import Bookmark, Comment, Like, Meme, MemeTag, Message, Tag, User, Warehouse, db
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
    
    meme:Meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")
    
    if to_comment_id is not None:
        to_comment:Comment = Comment.query.filter(Comment.comment_id==to_comment_id).first()
        if to_comment is None:
            return respond(ERR_COMMENT_NOT_FOUND, "回复的评论不存在")
    
    comment = Comment(
        meme_id=meme_id,
        to_comment_id=to_comment_id,
        user_id=current_user.user_id,
        content=content
    )
    db.session.add(comment)
    if meme.user_id != current_user.user_id:
        comment_message = Message(
            user_id = meme.user_id,
            id_type = "Meme",
            content = f"您上传的表情包有一个来自{current_user.username}的新评论",
            with_id = meme.meme_id
        )
        db.session.add(comment_message)
    if to_comment_id is not None and meme.user_id != to_comment.user_id and current_user.user_id != to_comment.user_id:
        to_comment_message = Message(
            user_id = to_comment.user_id,
            id_type = "Meme",
            content = f"{current_user.username}回复了您的评论",
            with_id = meme.meme_id
        )
        db.session.add(to_comment_message)

    db.session.commit()

    return respond(0, "评论成功", {"commentId": comment.comment_id})

@app.route("/api/comment-delete", methods=['POST'])
@login_required
def comment_delete():
    comment_id = request.form.get('commentId') or None

    for r in check_null_params(评论id=comment_id):
        return r
    
    comment = Comment.query.filter(and_(Comment.user_id==current_user.user_id, Comment.comment_id==comment_id)).first()

    if comment is None:
        return respond(ERR_COMMENT_NOT_FOUND, "评论不存在或无权操作")
    
    def recurrent_delete(top_comment: Comment):
        sub_comments = Comment.query.filter(Comment.to_comment_id==top_comment.comment_id).all()
        for sub_comment in sub_comments:
            recurrent_delete(sub_comment)
        db.session.delete(top_comment)

    recurrent_delete(comment) # recurrently delete all sub-comments

    db.session.commit()

    return respond(0, "删除成功")

@app.route("/api/comment-get", methods=['POST'])
@login_required
def comment_get():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r

    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")
    
    def recurrent_get(m_id: int, top_comment: Comment=None) -> dict:
        comment_list = []
        if top_comment is None:
            top_comments = Comment.query.filter(and_(Comment.meme_id==m_id, Comment.to_comment_id==None)).all()
            for top_comment in top_comments:
                comment_list.append(recurrent_get(m_id, top_comment))
            data_dict = {
                "comments": comment_list
            }
        else:
            sub_comments = Comment.query.filter(Comment.to_comment_id==top_comment.comment_id).all()
            for sub_comment in sub_comments:
                comment_list.append(recurrent_get(m_id, sub_comment))
            data_dict = {
                "commentId": top_comment.comment_id,
                "username": User.query.filter(User.user_id==top_comment.user_id).first().username,
                "content": top_comment.content,
                "commentTime": top_comment.comment_time,
                "comments": comment_list
            }

        return data_dict
        

    comment_data = recurrent_get(meme_id) # recurrently get all sub-comments

    return respond(0, "获取成功", comment_data)