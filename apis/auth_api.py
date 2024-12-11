import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from flask import session

from scripts.err import ERR_EMAIL_EXISTS, ERR_USER_BANNED, ERR_USER_NOT_FOUND, ERR_USERNAME_EXISTS, ERR_WRONG_FORMAT, ERR_WRONG_PASSWD
from scripts.init import app
from scripts.models import User, db
from scripts.utils import check_null_params, respond


auth_api = Blueprint('auth_api', __name__, template_folder='../templates')
current_user:User

@app.route("/api/auth-signup", methods=['POST'])
def auth_signup():
    username = request.form.get('username') or None
    email = request.form.get('email') or None
    password = request.form.get('password') or None

    for r in check_null_params(用户名=username, 邮箱=email, 密码=password):
        return r
    
    if not re.match(r'^[a-z0-9_]+$', username):
        return respond(ERR_WRONG_FORMAT, "用户名不合法")
    
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', email):
        return respond(ERR_WRONG_FORMAT, "邮箱不合法")
    
    if User.query.filter(User.username==username).first() != None:
        return respond(ERR_USERNAME_EXISTS, "此用户名已被占用！")
    
    if User.query.filter(User.email==email).first() != None:
        return respond(ERR_EMAIL_EXISTS, "此邮箱已被用于注册！")
    
    user = User(
        username=username,
        email=email,
    )
    user.set_password(password)
    from scripts.config import WIN
    user.profile_picture = "\\static\\images\\default.jpg" if WIN else "/static/images/default.jpg"

    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.user_id
    return respond(0, "注册成功！", {"userId": user.user_id})

@app.route("/api/auth-login", methods=['POST'])
def auth_login():
    name = request.form.get('username') or None
    password = request.form.get('password') or None

    for r in check_null_params(用户名或邮箱=name, 密码=password):
        return r

    if '@' in name:
        user:User = User.query.filter(User.email==name).first()
    else:
        user:User = User.query.filter(User.username==name).first()
    if user == None:
        return respond(ERR_USER_NOT_FOUND, "此用户不存在！")
    
    if not user.validate_password(password):
        return respond(ERR_WRONG_PASSWD, "密码错误！")
    
    if user.is_ban:
        return respond(ERR_USER_BANNED, "该用户已被封禁！")
    
    login_user(user)
        
    user_path = os.path.join(app.config['UPLOAD_FOLDER'], f"u{current_user.user_id}")

    if not os.path.exists(user_path):
        os.mkdir(user_path)

    session['user_id'] = user.user_id
    return respond(0, "登录成功！", {"userId": user.user_id})

@app.route("/api/auth-logout", methods=['POST'])
@login_required
def auth_logout():
    logout_user()

    return respond(0, "登出成功！")
