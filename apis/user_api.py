import os, sys, json,time
from scripts.init import app
from scripts.models import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import  Flask, Response, make_response, render_template, send_file, send_from_directory,url_for, flash, request, redirect
from flask import Blueprint

user_api = Blueprint('user_api', __name__, template_folder='templates')

@app.route("/api")
def api():
    return "this is api"