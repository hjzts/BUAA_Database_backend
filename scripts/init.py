import os
from flask import Flask
from flask import session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder=None)

CORS(app, supports_credentials=True)

app.secret_key = 'man what can i say mamba out'

DEVELOP = True
DB_URL = 'sqlite:///onlymemes.db' if DEVELOP else 'mysql+pymysql://u21374067:Aa773989@120.46.3.97:3306/h_db21374067'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SESSION_COOKIE_SIGNED'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True 

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['STATIC_FOLDER'] = '../static'

app.config['PORT'] = 5000

from scripts.config import WIN
UPLOAD_FOLDER = '.\\static\\images' if WIN else './static/images'
MEME_FOLDER = '.\\static\\images\\memes' if WIN else './static/images/memes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['INDEX_PATH'] = '.\\instance\\vector.index' if WIN else './instance/vector.index'





