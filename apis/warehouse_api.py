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
from scripts.models import Bookmark, Follow, Meme, MemeTag, Tag, User, Warehouse, db
from scripts.utils import allowed_file, check_null_params, respond


warehouse_api = Blueprint('warehouse_api', __name__, template_folder='../templates')
current_user:User

@app.route("/api/warehouse-create", methods=['POST'])
@login_required
def warehouse_create():
    name = request.form.get('name') or None

    for r in check_null_params(仓库名称=name):
        return r
    
    warehouse = Warehouse(
        user_id=current_user.user_id,
        name=name
    )
    db.session.add(warehouse)
    db.session.commit()

    return respond(0, "创建成功！", {"warehouseId": warehouse.warehouse_id})

@app.route("/api/warehouse-delete", methods=['POST'])
@login_required
def warehouse_delete():
    warehouse_id = request.form.get('warehouseId') or None

    for r in check_null_params(仓库id=warehouse_id):
        return r
    
    warehouse = Warehouse.query.filter(Warehouse.warehouse_id==warehouse_id).first()

    if warehouse is None:
        return respond(600101, "仓库不存在")
    
    Bookmark.query.filter(Bookmark.warehouse_id==warehouse_id).delete()
    db.session.delete(warehouse)
    db.session.commit()

    return respond(0, "删除成功！")

@app.route("/api/warehouse-add-bookmark", methods=['POST'])
@login_required
def warehouse_add_bookmark():
    meme_id = request.form.get('memeId') or None
    warehouse_id = request.form.get('warehouseId') or None

    for r in check_null_params(表情包id=meme_id, 仓库id=warehouse_id):
        return r
    
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(600101, "表情包不存在")

    warehouse = Warehouse.query.filter(Warehouse.warehouse_id==warehouse_id).first()

    if warehouse is None:
        return respond(600101, "仓库不存在")
    
    if warehouse.user_id != current_user.user_id:
        return respond(600102, "用户无权访问该仓库")
    
    bookmark = Bookmark.query.filter(
        and_(Bookmark.warehouse_id==warehouse_id, Bookmark.meme_id==meme_id)).first()
    
    if bookmark is not None:
        return respond(600103, "该收藏已存在")
    
    bookmark = Bookmark(
        meme_id=meme_id,
        warehouse_id=warehouse_id
    )

    db.session.add(bookmark)
    db.session.commit()

    return respond(0, "收藏成功！", {"bookmarkId": bookmark.bookmark_id})

@app.route("/api/warehouse-remove-bookmark", methods=['POST'])
@login_required
def warehouse_remove_bookmark():
    bookmark_id = request.form.get('bookmarkId') or None

    for r in check_null_params(收藏id=bookmark_id):
        return r
    
    bookmark = Bookmark.query.filter(Bookmark.bookmark_id==bookmark_id).first()

    if bookmark is None:
        return respond(600104, "该收藏不存在")

    warehouse = Warehouse.query.filter(Warehouse.warehouse_id==bookmark.warehouse_id).first()

    if warehouse is None:
        return respond(600101, "仓库不存在")

    if warehouse.user_id != current_user.user_id:
        return respond(600102, "用户无权访问该仓库")

    db.session.delete(bookmark)
    db.session.commit()

    return respond(0, "删除成功！")

@app.route("/api/warehouse-get-bookmarks", methods=['POST'])
@login_required
def warehouse_get_bookmark():
    warehouse_id = request.form.get('warehouseId') or None

    for r in check_null_params(仓库id=warehouse_id):
        return r

    warehouse = Warehouse.query.filter(Warehouse.warehouse_id==warehouse_id).first()

    if warehouse is None:
        return respond(600101, "仓库不存在")

    if warehouse.user_id != current_user.user_id and not Follow.query.filter(
        and_(Follow.followee_id==warehouse.user_id, Follow.follower_id==current_user.user_id)).first() is not None:
        return respond(600102, "用户无权访问未关注者的仓库")
    
    bookmarks_data = {
        "bookmarks":[{
            "bookmarkId" : bookmark.bookmark_id,
            "memeId" : bookmark.meme_id,
            "warehouseId" : bookmark.warehouse_id,
            "bookmarkTime" : bookmark.bookmark_time,
        } for bookmark in Bookmark.query.filter(Bookmark.warehouse_id==warehouse_id).all()]
    }

    return respond(0, "查询成功", bookmarks_data)