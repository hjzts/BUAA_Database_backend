import email
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from sqlalchemy import true
from werkzeug.utils import secure_filename

from scripts.err import ERR_MESSAGE_NOT_FOUND, ERR_USER_NOT_FOUND, ERR_WRONG_FORMAT
from scripts.init import app
from scripts.models import User, db, Message
from scripts.utils import allowed_file, check_null_params, clearfile, respond

message_api = Blueprint('message_api', __name__, template_folder='../templates')


@app.route("/api/message-get-user-message", methods=['POST'])
@login_required
def get_user_message():

    message_data = {  
        "messages":[{
            "messageId":message.message_id,
            "type": message.type,
            "content":message.content,
            "withId": message.with_id
        } for message in Message.query.filter(Message.user_id==current_user.user_id).all()]
    }

    return respond(0, "查询成功", message_data)

@app.route("/api/message-read-message", methods=['POST'])
@login_required
def read_message():

    message_id = request.form.get('messageId') or None

    for r in check_null_params(消息id=message_id):
        return r

    message:Message = Message.query.filter(Message.message_id==message_id).first()

    if message is None:
        return respond(ERR_MESSAGE_NOT_FOUND, "消息不存在")
    
    message.read = True

    db.session.commit()

    return respond(0, "消息已读")