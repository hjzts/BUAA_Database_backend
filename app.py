import os
import threading
from flask import Flask, Response, render_template, request
import requests

from scripts.init import app
from scripts.models import db

from apis.auth_api import user_api
app.register_blueprint(user_api)

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



if __name__ == '__main__':
    print("start server")
    app.run(debug=True, port=5000)
