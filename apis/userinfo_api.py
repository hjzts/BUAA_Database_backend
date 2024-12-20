import email
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from werkzeug.utils import secure_filename

from scripts.err import ERR_USER_NOT_FOUND, ERR_WRONG_FORMAT
from scripts.init import app
from scripts.models import User, db
from scripts.utils import allowed_file, check_null_params, clearfile, respond

userinfo_api = Blueprint('userinfo_api', __name__, template_folder='../templates')
current_user:User

@app.route("/api/userinfo-get-current-user", methods=['POST'])
@login_required
def user_info():

    info_data={
        "uid": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "profile_picture": current_user.profile_picture,
        "bio": current_user.bio,
        "currency": current_user.hugo_coin,
        "signup_time": current_user.signup_time
    }

    return respond(0, "查询成功", info_data)

@app.route("/api/userinfo-is-admin", methods=['POST'])
@login_required
def userinfo_is_admin():
    is_admin =  (current_user.username=="admin")
    
    info_data={
        "is_admin":is_admin # true or false
    }
    
    return respond(0, "查询成功", info_data)

@app.route("/api/userinfo-get-user", methods=['POST'])
def get_user():

    user_id = request.form.get('userId') or None

    for r in check_null_params(用户id=user_id):
        return r

    user:User = User.query.filter(User.user_id==user_id).first()

    if user is None:
        return respond(ERR_USER_NOT_FOUND, "用户不存在")

    info_data={
        "uid": user.user_id,
        "username": user.username,
        "email": user.email,
        "profile_picture": user.profile_picture,
        "bio": user.bio,
        "currency": user.hugo_coin,
        "signup_time": user.signup_time
    }

    return respond(0, "查询成功", info_data)

@app.route("/api/userinfo-update-avatar", methods=['POST'])
@login_required
def update_avatar():
    avatar = request.files.get('avatar') or None

    for r in check_null_params(头像=avatar):
        return r

    if not allowed_file(avatar.filename):
        return respond(ERR_WRONG_FORMAT, "图片格式错误！")
    
    user_path = os.path.join(app.config['UPLOAD_FOLDER'], f"u{current_user.user_id}")
    clearfile(user_path)
    
    filename = secure_filename(avatar.filename)
    filepath = os.path.join(user_path, filename)
    avatar.save(filepath)

    current_user.profile_picture = filepath
    db.session.commit()

    return respond(0, "头像上传成功！", {"avatar_url": filepath})

@app.route("/api/userinfo-update-email", methods=['POST'])
@login_required
def update_email():
    email = request.form.get('email') or None

    for r in check_null_params(邮箱=email):
        return r

    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', email):
        return respond(ERR_WRONG_FORMAT, "邮箱不合法")
    
    current_user.email = email
    db.session.commit()

    return respond(0, "邮箱已更新！", {"email": email})


@app.route("/api/userinfo-update-username", methods=['POST'])
@login_required
def update_username():
    username = request.form.get('username') or None

    for r in check_null_params(用户名=username):
        return r

    if not re.match(r'^[a-z0-9_]+$', username):
        return respond(ERR_WRONG_FORMAT, "用户名不合法")
    
    current_user.username = username
    db.session.commit()

    return respond(0, "用户名已更新！", {"username": username})

@app.route("/api/userinfo-update-bio", methods=['POST'])
@login_required
def update_bio():
    bio = request.form.get('bio') or None

    for r in check_null_params(个人简介=bio):
        return r
    
    current_user.bio = bio
    db.session.commit()

    return respond(0, "个人简介已更新！", {"bio": bio})   

@app.route("/api/userinfo-update-password", methods=['POST'])
@login_required
def update_password():
    password = request.form.get('password') or None
    new_password = request.form.get('new_password') or None
    
    for r in check_null_params(原密码=password, 新密码=new_password):
        return r
    
    if not current_user.validate_password(password):
        return respond(ERR_WRONG_FORMAT, "原密码错误！")
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return respond(0, "密码已更新！", {"new_password": new_password})
    