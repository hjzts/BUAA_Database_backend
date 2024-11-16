from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DEVELOP = True
DB_URL = 'sqlite:///onlymemes.db' if DEVELOP else 'mysql+pymysql://u21374067:Aa773989@120.46.3.97:3306/h_db21374067'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

