import re
import os, sys, json, time
from tkinter import NO
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import  Flask, Response, make_response, render_template, send_file, send_from_directory,url_for, flash, request, redirect
from flask import Blueprint
from datetime import datetime

from scripts.init import app
from scripts.models import User, db
from scripts.utils import check_null_params, respond


user_api = Blueprint('user_api', __name__, template_folder='../templates')

login_manager = LoginManager(app)
current_user:User

@app.route("/api", methods=['GET','POST'])
def api():
    return "this is where api lives"

@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    return user


@app.route("/api/auth-signup", methods=['POST'])
def user_signup():
    username = request.form.get('username') or None
    email = request.form.get('email') or None
    password = request.form.get('password') or None

    for r in check_null_params(username=username, email=email, password=password):
        return r
    
    if not re.match(r'^[a-z0-9_]+$', username):
        return respond(100998, {"info":"用户名不合法"})
    
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', email):
        return respond(100998, {"info":"邮箱不合法"})
    
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
def user_login():
    name = request.form['username']
    password = request.form['password']

    if '@' in name:
        user:User = User.query.filter(User.email==name).first()
    else:
        user:User = User.query.filter(User.username==name).first()
    if user == None:
        return respond(1, {"info":"此用户不存在！"})
    
    if user.validate_password(password):
        login_user(user)
    else:
        return respond(1, {"info":"密码错误！"})

    return respond(0, {'info':"登录成功！"})

@app.route("/api/user-info", methods=['POST'])
@login_required
def user_info():

    info_data={
        "uid": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "profile_picture": current_user.profile_picture,
        "bio": current_user.bio,
        "currency": current_user.hugo_coin,
        "signup_date": current_user.signup_date
    }

    return respond(0, info_data)