import os, sys, json, time

from scripts.err import ERR_NULL_INPUT
from scripts.init import ALLOWED_EXTENSIONS

def respond(code:int, data:dict=None):
    ret_json = {
        'success': "true" if code == 0 else "false",
        'errCode': code,
        'data' : data or {}
    }
    return ret_json

def check_null_params(**kwargs):
    error_list = []
    for k,v in kwargs.items():
        if v is None:
            error_list.append(respond(ERR_NULL_INPUT, {"info":f"{k}不能为空"}))

    return error_list

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clearfile(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 如果是文件，删除文件
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # 删除文件或符号链接