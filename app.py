import argparse
import os
import shutil
import threading
from flask import Flask, Response, render_template, request, send_file, send_from_directory, session
from flask_login import LoginManager
import requests

from scripts.init import UPLOAD_FOLDER, app
from scripts.utils import init_env
from scripts.models import db
from scripts.faiss_img import index
from scripts.test import test

from apis.auth_api import auth_api
from apis.userinfo_api import userinfo_api
from apis.meme_api import meme_api
from apis.warehouse_api import warehouse_api
from apis.like_api import like_api
from apis.comment_api import comment_api
from apis.post_api import post_api
from apis.report_api import report_api
from apis.follow_api import follow_api
from apis.admin_api import admin_api
from apis.message_api import message_api

app.register_blueprint(auth_api)
app.register_blueprint(userinfo_api)
app.register_blueprint(meme_api)
app.register_blueprint(warehouse_api)
app.register_blueprint(like_api)
app.register_blueprint(comment_api)
app.register_blueprint(post_api)
app.register_blueprint(report_api)
app.register_blueprint(follow_api)
app.register_blueprint(admin_api)
app.register_blueprint(message_api)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(403)
def internal_server_error(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def internal_server_error(error):
    return render_template('404.html'), 404

@app.errorhandler(410)
def internal_server_error(error):
    return render_template('410.html'), 410

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    path = os.path.join(app.config['STATIC_FOLDER'], filename)
    return send_file(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="args")
    parser.add_argument('-d', action='store_true', help='drop all')
    parser.add_argument('-p', type=int, default="5000")
    parser.add_argument('-t', action='store_true', help='test')
    args = parser.parse_args()

    app.config['PORT'] = args.p

    if args.t:
        test()
        exit(0)

    with app.app_context():
        if args.d:
            db.drop_all()
            db.create_all()
            if os.path.isdir(UPLOAD_FOLDER):
                shutil.rmtree(UPLOAD_FOLDER)
            os.remove(app.config['INDEX_PATH'])

    init_env()

    print("start server")
    app.run(debug=True, port=app.config['PORT'])
