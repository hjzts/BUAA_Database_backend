import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  render_template, request
from flask import Blueprint
from functools import wraps
from sqlalchemy import and_, or_

from requests import delete

from scripts.err import ERR_BAN_ADMIN, ERR_MEME_NOT_FOUND, ERR_REPORT_NOT_FOUND, ERR_USER_NOT_FOUND, ERR_WRONG_FORMAT
from scripts.faiss_img import remove_image
from scripts.init import app
from scripts.models import Meme, Message, Report, User, db, Tag, MemeTag
from scripts.utils import check_null_params, respond


admin_api = Blueprint('admin_api', __name__, template_folder='../templates')
current_user:User

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            return render_template('403.html'), 403  # 返回403 Forbidden错误
        return func(*args, **kwargs)
    return decorated_view

@app.route("/api/admin-get-all-users", methods=['POST'])
@admin_required
def admin_get_all_users():
    users_data = {
        "users": [{
            "userId": user.user_id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.profile_picture,
            "bio": user.bio,
            "signupTime": user.signup_time,
            "currency": user.hugo_coin,
            "banned": user.is_ban,
        } for user in User.query.all()]
    }

    return respond(0, "获取成功", users_data)


@app.route("/api/admin-get-all-blocked-users", methods=['POST'])
@admin_required
def admin_get_all_blocked_users():
    users_data = {
        "users": [{
            "userId": user.user_id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.profile_picture,
            "bio": user.bio,
            "signupTime": user.signup_time,
            "currency": user.hugo_coin,
            "banned": user.is_ban,
        } for user in User.query.filter(User.is_ban==True).all()]
    }

    return respond(0, "获取成功", users_data)

@app.route("/api/admin-get-all-unblocked-users", methods=['POST'])
@admin_required
def admin_get_all_unblocked_users():
    users_data = {
        "users": [{
            "userId": user.user_id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.profile_picture,
            "bio": user.bio,
            "signupTime": user.signup_time,
            "currency": user.hugo_coin,
            "banned": user.is_ban,
        } for user in User.query.filter(User.is_ban==False).all()]
    }

    return respond(0, "获取成功", users_data)

@app.route("/api/admin-block-user", methods=['POST'])
@admin_required
def admin_block_user():
    user_id = request.form.get('userId') or None

    for r in check_null_params(用户id=user_id):
        return r

    user:User = User.query.filter(User.user_id==user_id).first()
    if user == None:
        return respond(ERR_USER_NOT_FOUND, "此用户不存在！")

    if user.username == 'admin':
        return respond(ERR_BAN_ADMIN, "管理员不能封禁自己！")
    
    if not user.is_ban:
        user.is_ban = True

        ban_message = Message(
            user_id = user.user_id,
            id_type = "normal",
            content = "您已被封禁！"
        )
        db.session.add(ban_message)
            
        db.session.commit()

    return respond(0, "封禁成功！")

@app.route("/api/admin-unblock-user", methods=['POST'])
@admin_required
def admin_unblock_user():
    user_id = request.form.get('userId') or None

    for r in check_null_params(用户id=user_id):
        return r

    user:User = User.query.filter(User.user_id==user_id).first()
    if user == None:
        return respond(ERR_USER_NOT_FOUND, "此用户不存在！")
    
    if user.is_ban:
        user.is_ban = False

        unban_message = Message(
            user_id = user.user_id,
            id_type = "normal",
            content = "您已被解封！"
        )
        db.session.add(unban_message)
        
        db.session.commit()

    return respond(0, "解封成功！")

@app.route("/api/admin-get-all-memes", methods=['POST'])
@admin_required
def admin_get_all_memes():
    memes = Meme.query.all()

    if memes is None:
        return respond(ERR_MEME_NOT_FOUND, "仓库中没有表情包")

    meme_data = [{
        "memeId" : meme.meme_id,
        "caption": meme.caption,
        "imageUrl" : meme.image_url,
        "uploadUsername" : User.query.filter(User.user_id==meme.user_id).first().username,
        "uploadUserId" : meme.user_id,
        "uploadTime" : meme.upload_time,
        "views" : meme.views,
        "likes" : meme.likes,
        "isBlock": meme.is_block,
        "tags":[{
            "tagId": tag.tag_id,
            "tagName": tag.name
        } for tag in Tag.query.join(MemeTag,
            and_(MemeTag.meme_id==meme.meme_id, MemeTag.tag_id==Tag.tag_id)).all()]
    } for meme in memes]


    return respond(0, "查询成功", meme_data)


@app.route("/api/admin-get-all-blocked-memes", methods=['POST'])
@admin_required
def admin_get_all_blocked_memes():
    memes = Meme.query.filter(Meme.is_block==True).all()

    if memes is None:
        return respond(ERR_MEME_NOT_FOUND, "仓库中没有表情包")

    meme_data = {
        "memes": [{
        "memeId" : meme.meme_id,
        "caption": meme.caption,
        "imageUrl" : meme.image_url,
        "uploadUsername" : User.query.filter(User.user_id==meme.user_id).first().username,
        "uploadUserId" : meme.user_id,
        "uploadTime" : meme.upload_time,
        "views" : meme.views,
        "likes" : meme.likes,
        "isBlock": meme.is_block,
        "tags":[{
            "tagId": tag.tag_id,
            "tagName": tag.name
        } for tag in Tag.query.join(MemeTag,
            and_(MemeTag.meme_id==meme.meme_id, MemeTag.tag_id==Tag.tag_id)).all()]
        } for meme in memes]
    }


    return respond(0, "查询成功", meme_data)

@app.route("/api/admin-get-all-unblocked-memes", methods=['POST'])
@admin_required
def admin_get_all_unblocked_memes():
    memes = Meme.query.filter(Meme.is_block==False).all()

    if memes is None:
        return respond(ERR_MEME_NOT_FOUND, "仓库中没有表情包")

    meme_data = [{
        "memeId" : meme.meme_id,
        "caption": meme.caption,
        "imageUrl" : meme.image_url,
        "uploadUsername" : User.query.filter(User.user_id==meme.user_id).first().username,
        "uploadUserId" : meme.user_id,
        "uploadTime" : meme.upload_time,
        "views" : meme.views,
        "likes" : meme.likes,
        "isBlock": meme.is_block,
        "tags":[{
            "tagId": tag.tag_id,
            "tagName": tag.name
        } for tag in Tag.query.join(MemeTag,
            and_(MemeTag.meme_id==meme.meme_id, MemeTag.tag_id==Tag.tag_id)).all()]
    } for meme in memes]


    return respond(0, "查询成功", meme_data)

@app.route("/api/admin-block-meme", methods=['POST'])
@admin_required
def admin_block_meme():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r

    meme:Meme = Meme.query.filter(Meme.meme_id==meme_id).first()
    if meme == None:
        return respond(ERR_MEME_NOT_FOUND, "此表情包不存在！")
    
    if not meme.is_block:
        meme.is_block = True
        ban_message = Message(
            user_id = meme.user_id,
            id_type = "Meme",
            content = "您上传的表情包已被封禁！",
            with_id = meme.meme_id
        )
            
        db.session.commit()

    return respond(0, "封禁成功！")

@app.route("/api/admin-unblock-meme", methods=['POST'])
@admin_required
def admin_unblock_meme():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r

    meme:Meme = Meme.query.filter(Meme.meme_id==meme_id).first()
    if meme == None:
        return respond(ERR_MEME_NOT_FOUND, "此表情包不存在！")
    
    if meme.is_block:
        meme.is_block = False
        unban_message = Message(
            user_id = meme.user_id,
            id_type = "Meme",
            content = "您上传的表情包已被解封！",
            with_id = meme.meme_id
        )            
        
        db.session.commit()

    return respond(0, "解封成功！")

@app.route("/api/admin-get-user-num", methods=['POST'])
@admin_required
def admin_get_user_num():
    return respond(0, "查询成功", {"num":User.query.count()})

@app.route("/api/admin-get-report-num", methods=['POST'])
@admin_required
def admin_get_report_num():
    return respond(0, "查询成功", {"num":Report.query.count()})


@app.route("/api/admin-get-all-reports", methods=['POST'])
@login_required
def admin_get_all_reports():
    reports_data = {
        "reports": [{
            "reportId": report.report_id,
            "memeId": report.meme_id,
            "userId": report.user_id,
            "reason": report.reason,
            "reportTime": report.report_time,
            "status": report.status
        } for report in Report.query.all()]
    }

    return respond(0, "获取成功", reports_data)

@app.route("/api/admin-get-report", methods=['POST'])
@login_required
def admin_get_report():
    report_id = request.form.get('reportId') or None

    for r in check_null_params(举报id=report_id):
        return r

    report:Report = Report.query.filter(Report.report_id==report_id).first()
    if report == None:
        return respond(ERR_REPORT_NOT_FOUND, "此举报不存在！")

    report_data = {
        "reportId": report.report_id,
        "memeId": report.meme_id,
        "userId": report.user_id,
        "reason": report.reason,
        "reportTime": report.report_time,
        "status": report.status
    }

    return respond(0, "获取成功", report_data)

@app.route("/api/admin-deal-with-report", methods=['POST'])
@login_required
def admin_deal_with_report():
    report_id = request.form.get('reportId') or None

    for r in check_null_params(举报id=report_id):
        return r

    report:Report = Report.query.filter(Report.report_id==report_id).first()
    if report == None:
        return respond(ERR_REPORT_NOT_FOUND, "此举报不存在！")

    meme = Meme.query.filter(Meme.meme_id==report.meme_id).first()
    if meme is not None:
        remove_image(meme.meme_id)
        db.session.delete(meme)

    report.status = 'resolved'

    db.session.commit()

    return respond(0, "处理成功")