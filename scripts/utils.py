import os, sys, json, time

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
            error_list.append(respond(100999, {"info":f"{k}不能为空"}))

    return error_list