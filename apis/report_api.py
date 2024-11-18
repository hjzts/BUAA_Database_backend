from random import randint
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from sqlalchemy import and_, or_
from datetime import datetime

from scripts.err import ERR_WRONG_FORMAT
from scripts.init import MEME_FOLDER, app
from scripts.models import Bookmark, Comment, Like, Meme, MemeTag, Post, PostBounty, Report, Tag, User, Warehouse, db
from scripts.utils import allowed_file, check_null_params, respond


report_api = Blueprint('report_api', __name__, template_folder='../templates')
current_user:User

@app.route("/api/report-issue", methods=['POST'])
@login_required
def report_issue():
    meme_id = request.form.get('memeId') or None
    reason = request.form.get('reason') or None
    is_anonymous = request.form.get('isAnonymous') == 'true'

    for r in check_null_params(表情包id=meme_id, 原因=reason):
        return r
    
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(1000101, "表情包不存在")
    
    report = Report(
        meme_id=meme_id,
        user_id=current_user.user_id if not is_anonymous else None,
        reason=reason,
    )
    
    db.session.add(report)

    db.session.commit()
    
    return respond(0, "举报成功", {"reportId": report.report_id})

