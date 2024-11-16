import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint

from scripts.err import ERR_WRONG_FORMAT
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
        return respond(ERR_WRONG_FORMAT, {"info":"用户名不合法"})
    
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', email):
        return respond(ERR_WRONG_FORMAT, {"info":"邮箱不合法"})
    
    if User.query.filter(User.username==username).first() != None:
        return respond(200201, {"info":"此用户名已被占用！"})
    
    if User.query.filter(User.email==email).first() != None:
        return respond(200202, {"info":"此邮箱已被用于注册！"})
    
    user = User(
        username=username,
        email=email,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return respond(0, {"info":"注册成功！"})

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
        return respond(200101, {"info":"此用户不存在！"})
    
    if not user.validate_password(password):
        return respond(200101, {"info":"密码错误！"})
    
    login_user(user)
        
    user_path = os.path.join(app.config['UPLOAD_FOLDER'], f"u{current_user.user_id}")

    if not os.path.exists(user_path):
        os.mkdir(user_path)

    return respond(0, {'info':"登录成功！"})

@app.route("/api/auth-logout", methods=['POST'])
@login_required
def auth_logout():
    logout_user()

    return respond(0, {'info':"登出成功！"})
