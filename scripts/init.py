import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = 'man what can i say mamba out'

DEVELOP = True
DB_URL = 'sqlite:///onlymemes.db' if DEVELOP else 'mysql+pymysql://u21374067:Aa773989@120.46.3.97:3306/h_db21374067'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = './static/images'
MEME_FOLDER = './static/images/memes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




