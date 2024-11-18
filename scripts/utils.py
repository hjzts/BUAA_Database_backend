import os, sys, json, time

from scripts.err import ERR_NULL_INPUT
from scripts.init import app, ALLOWED_EXTENSIONS, UPLOAD_FOLDER, MEME_FOLDER
from scripts.models import db, User

def init_env():
    # 确保上传文件夹存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if not os.path.exists(MEME_FOLDER):
        os.makedirs(MEME_FOLDER)

    # 创建管理员用户
    with app.app_context():
        if User.query.filter(User.username=="admin").first() is None:
            admin = User(
                username="admin",
                email="admin@ad.min",
            )
            admin.set_password("root")
            db.session.add(admin)
            db.session.commit()
        

def respond(code:int, info:str, data:dict=None):
    data_dict = data or {}
    ret_json = {
        'data' : data_dict,
        'errCode': code,
        'info' :info,
        'success': "true" if code == 0 else "false",
    }
    return ret_json

def check_null_params(**kwargs):
    error_list = []
    for k,v in kwargs.items():
        if v is None:
            error_list.append(respond(ERR_NULL_INPUT, f"{k}不能为空"))

    return error_list

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clearfile(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 如果是文件，删除文件
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # 删除文件或符号链接