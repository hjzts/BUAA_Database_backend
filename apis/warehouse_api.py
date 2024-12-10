from logging import WARNING
from random import randint
import re
import os, sys, json, time
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from sqlalchemy import and_, or_
from datetime import datetime

from scripts.err import ERR_ACCESS_DENIED, ERR_BOOKMARK_EXISTS, ERR_BOOKMARK_NOT_FOUND, ERR_MEME_NOT_FOUND, ERR_WAREHOUSR_NOT_FOUND, ERR_WRONG_FORMAT,ERR_BAD_PERMMISION
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
        return respond(ERR_WAREHOUSR_NOT_FOUND, "仓库不存在")
    
    if warehouse.user_id != current_user.user_id:
        return respond(ERR_BAD_PERMMISION, "用户不能删除不是自己的仓库")
    
    Bookmark.query.filter(Bookmark.warehouse_id==warehouse_id).delete()
    db.session.delete(warehouse)
    db.session.commit()

    return respond(0, "删除成功！")

@app.route("/api/warehouse-get", methods=['POST'])
@login_required
def warehouse_get():
    warehouse_data = {
        "warehouses":[{
            "warehouseId":warehouse.warehouse_id,
            "name": warehouse.name,
            "capacity":warehouse.capacity,
            "memeCount": Bookmark.query.filter(Bookmark.warehouse_id==warehouse.warehouse_id).count(),
            "userId":warehouse.user_id,
            "username":User.query.get(warehouse.user_id).username
        } for warehouse in Warehouse.query.filter(or_(Warehouse.user_id==current_user.user_id, 
                Follow.query.filter(and_(Follow.followee_id==Warehouse.user_id,
                                          Follow.follower_id==current_user.user_id)).exists()
        ))]
    }

    return respond(0, "查询成功！", warehouse_data)

@app.route("/api/warehouse-update-name", methods=["POST"])
@login_required
def warehouse_update_name():
    warehouse_id = request.form.get('warehouseId') or None
    new_warehouse_name = request.form.get('newWarehouseName') or None
    
    for r in check_null_params(仓库id=warehouse_id):
        return r

    warehouse = Warehouse.query.filter(Warehouse.warehouse_id==warehouse_id).first()
    
    if warehouse is None:
        return respond(ERR_WAREHOUSR_NOT_FOUND, "仓库不存在")
    
    if warehouse.user_id != current_user.user_id:
        return respond(ERR_ACCESS_DENIED, "用户无权访问该仓库")
    
    warehouse_name = request.form.get('warehouseName') or None
    if warehouse.name != warehouse_name:
        return respond(ERR_ACCESS_DENIED, "仓库名不匹配")
    
    warehouse.name = new_warehouse_name
    db.session.commit()
    
    return respond(0, "仓库名修改成功! ", {"new_warehouse_name": new_warehouse_name})

@app.route("/api/warehouse-get-own",methods=["POST"])
@login_required
def warehouse_get_own():
    warehouse_data = {
        "warehouses":[{
            "warehouseId":warehouse.warehouse_id,
            "name": warehouse.name,
            "capacity":warehouse.capacity,
            "memeCount": Bookmark.query.filter(Bookmark.warehouse_id==warehouse.warehouse_id).count(),
            "userId":warehouse.user_id,
            "username":User.query.get(warehouse.user_id).username
        } for warehouse in Warehouse.query.filter(Warehouse.user_id==current_user.user_id).all()
        ]
    }

    return respond(0, "查询成功！", warehouse_data)

@app.route("/api/warehouse-add-bookmark", methods=['POST'])
@login_required
def warehouse_add_bookmark():
    meme_id = request.form.get('memeId') or None
    warehouse_id = request.form.get('warehouseId') or None

    for r in check_null_params(表情包id=meme_id, 仓库id=warehouse_id):
        return r
    
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")

    warehouse = Warehouse.query.filter(Warehouse.warehouse_id==warehouse_id).first()

    if warehouse is None:
        return respond(ERR_WAREHOUSR_NOT_FOUND, "仓库不存在")
    
    if warehouse.user_id != current_user.user_id:
        return respond(ERR_ACCESS_DENIED, "用户无权访问该仓库")
    
    bookmark = Bookmark.query.filter(
        and_(Bookmark.warehouse_id==warehouse_id, Bookmark.meme_id==meme_id)).first()
    
    if bookmark is not None:
        return respond(ERR_BOOKMARK_EXISTS, "该收藏已存在")
    
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
        return respond(ERR_BOOKMARK_NOT_FOUND, "该收藏不存在")

    warehouse = Warehouse.query.filter(Warehouse.warehouse_id==bookmark.warehouse_id).first()

    if warehouse is None:
        return respond(ERR_WAREHOUSR_NOT_FOUND, "仓库不存在")

    if warehouse.user_id != current_user.user_id:
        return respond(ERR_ACCESS_DENIED, "用户无权访问该仓库")

    db.session.delete(bookmark)
    db.session.commit()

    return respond(0, "删除成功！")

@app.route("/api/warehouse-get-bookmarks", methods=['POST'])
@login_required
def warehouse_get_bookmarks():
    warehouse_id = request.form.get('warehouseId') or None

    for r in check_null_params(仓库id=warehouse_id):
        return r

    warehouse = Warehouse.query.filter(Warehouse.warehouse_id==warehouse_id).first()

    if warehouse is None:
        return respond(ERR_WAREHOUSR_NOT_FOUND, "仓库不存在")

    if warehouse.user_id != current_user.user_id and not Follow.query.filter(
        and_(Follow.followee_id==warehouse.user_id, Follow.follower_id==current_user.user_id)).first() is not None:
        return respond(ERR_ACCESS_DENIED, "用户无权访问未关注者的仓库")
    
    bookmarks_data = {
        "name": warehouse.name,
        "capacity":warehouse.capacity,
        "bookmarks":[{
            "bookmarkId" : bookmark.bookmark_id,
            "memeId" : bookmark.meme_id,
            "warehouseId" : bookmark.warehouse_id,
            "bookmarkTime" : bookmark.bookmark_time,
            "likes": Meme.query.get(bookmark.meme_id).likes,
            "uploaderId": Meme.query.get(bookmark.meme_id).user_id,
            "uploaderName": User.query.get(Meme.query.get(bookmark.meme_id).user_id).username,
            "tags": [tag.name for tag in Tag.query.join(MemeTag).filter(MemeTag.meme_id == bookmark.meme_id)]
        } for bookmark in Bookmark.query.filter(Bookmark.warehouse_id==warehouse_id).all()]
    }

    return respond(0, "查询成功", bookmarks_data)