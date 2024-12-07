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

message_api = Blueprint('message_api', __name__, template_folder='../templates')


@app.route("/api/message-get-user-message", methods=['POST'])
@login_required
def get_user_message():

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