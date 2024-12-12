from random import randint
import re
import os, sys, json, time
from bs4 import BeautifulSoup
from flask_login import login_user, login_required, logout_user, current_user
from flask import  request
from flask import Blueprint
from numpy import indices
import requests
from sqlalchemy import and_, or_
from torch import NoneType
from werkzeug.utils import secure_filename
from datetime import datetime

from scripts.err import ERR_MEME_NOT_FOUND, ERR_POST_NOT_FOUND, ERR_WRONG_FORMAT
from scripts.init import MEME_FOLDER, app
from scripts.models import Meme, MemeTag, Message, Tag, User, Post, db
from scripts.utils import allowed_file, check_null_params, respond
from scripts.faiss_img import add_img_to_index, remove_image, search_similar_img


meme_api = Blueprint('meme_api', __name__, template_folder='../templates')
current_user:User

@app.route("/api/meme-upload", methods=['POST'])
@login_required
def meme_upload():
    meme_img = request.files.get('meme') or None
    caption = request.form.get('caption') or None
    tags = [t.strip() for t in request.form.get('tags').replace('；',';').split(';')] or None
    post_id = request.form.get('postId') or None

    for r in check_null_params(图片=meme_img, 标签=tags):
        return r
    
    if not allowed_file(meme_img.filename):
        return respond(ERR_WRONG_FORMAT, "图片格式错误！")
    
    post:Post = None
    if post_id is not None:
        post = Post.query.filter(Post.post_id==post_id).first()
        if post is None:
            return respond(ERR_POST_NOT_FOUND, "目标请求贴不存在！")
    
    filepath = os.path.join(MEME_FOLDER, datetime.now().strftime("%Y%m%d%H%M%S") +\
                             "%04x." % randint(0,16**4) + meme_img.filename.split('.')[-1])
    while os.path.exists(filepath):
        filepath = os.path.join(MEME_FOLDER, datetime.now().strftime("%Y%m%d%H%M%S") +\
                                 "%04x." % randint(0,16**4) + meme_img.filename.split('.')[-1])

    meme_img.save(filepath)
    
    meme = Meme(
        user_id=current_user.user_id,
        caption=caption,
        image_url=filepath
    )
    db.session.add(meme)
    db.session.commit()

    if tags is not None:
        for tag_name in tags:
            tag = Tag.query.filter(Tag.name==tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.commit()
            memeTag = MemeTag(
                meme_id=meme.meme_id,
                tag_id=tag.tag_id
            )
            db.session.add(memeTag)

    add_img_to_index(image_path=meme.image_url, image_id=meme.meme_id)

    current_user.hugo_coin += 1
    db.session.commit()

    # response post
    if post is not None:
        current_user.hugo_coin += post.bounty

        post_message = Message(
            user_id = post.user_id,
            id_type = "Meme",
            content = f"{current_user.username}响应了您的请求贴！",
            with_id = meme.meme_id
        )
        db.session.add(post_message)

        db.session.delete(post)

        db.session.commit()

    return respond(0, "上传成功！", {"memeId": meme.meme_id})

@app.route("/api/meme-delete", methods=['POST'])
@login_required
def meme_delete():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r
    
    meme = Meme.query.filter(and_(Meme.meme_id==meme_id, Meme.user_id==current_user.user_id)).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在或无权操作")
    
    remove_image(meme_id)
    db.session.delete(meme)
    db.session.commit()

    return respond(0, "删除成功")


@app.route("/api/meme-get-total-num", methods=['POST'])
@login_required
def meme_get_total_num():
    return respond(0, "查询成功", {"num":Meme.query.count()})

@app.route("/api/meme-get-self-num", methods=['POST'])
@login_required
def meme_get_self_num():
    return respond(0, "查询成功", {"num":Meme.query.filter(Meme.user_id==current_user.user_id).count()})

@app.route("/api/meme-view", methods=['POST'])
@login_required
def meme_view():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r
    
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")

    meme.views += 1

    db.session.commit()

    return respond(0, "更新成功", {"views": meme.views})

@app.route("/api/meme-get", methods=['POST'])
@login_required
def meme_get():
    meme_id = request.form.get('memeId') or None

    for r in check_null_params(表情包id=meme_id):
        return r
    
    meme = Meme.query.filter(Meme.meme_id==meme_id).first()

    if meme is None:
        return respond(ERR_MEME_NOT_FOUND, "表情包不存在")

    meme_data = {
        "memeId" : meme.meme_id,
        "caption": meme.caption,
        "imageUrl" : meme.image_url,
        "uploadUsername" : User.query.filter(User.user_id==meme.user_id).first().username,
        "uploadUserId" : meme.user_id,
        "uploadTime" : meme.upload_time,
        "views" : meme.views,
        "likes" : meme.likes,
        "isBlock": meme.is_block,
        "tags":[{
            "tagId": tag.tag_id,
            "tagName": tag.name
        } for tag in Tag.query.join(MemeTag,
            and_(MemeTag.meme_id==meme.meme_id, MemeTag.tag_id==Tag.tag_id)).all()]
    }


    return respond(0, "查询成功", meme_data)

@app.route("/api/meme-get-own", methods=['POST'])
@login_required
def meme_get_own():
    memes = Meme.query.filter(Meme.user_id==current_user.user_id).order_by(Meme.upload_time.desc()).all()

    if memes is None:
        return respond(ERR_MEME_NOT_FOUND, "该用户没有表情包")

    meme_data = [{
        "memeId" : meme.meme_id,
        "caption": meme.caption,
        "imageUrl" : meme.image_url,
        "uploadUsername" : User.query.filter(User.user_id==meme.user_id).first().username,
        "uploadUserId" : meme.user_id,
        "uploadTime" : meme.upload_time,
        "views" : meme.views,
        "likes" : meme.likes,
        "isBlock": meme.is_block,
        "tags":[{
            "tagId": tag.tag_id,
            "tagName": tag.name
        } for tag in Tag.query.join(MemeTag,
            and_(MemeTag.meme_id==meme.meme_id, MemeTag.tag_id==Tag.tag_id)).all()]
    } for meme in memes]


    return respond(0, "查询成功", meme_data)

@app.route("/api/meme-get-batch", methods=['POST'])
@login_required
def meme_get_batch():
    page_size = request.form.get('pagesize') or None
    page_idx = request.form.get('page') or None

    for r in check_null_params(每页图片数量=page_size, 页号=page_idx):
        return r
    
    if not page_size.isdecimal():
        return respond(ERR_WRONG_FORMAT, "每页图片数量不是正整数！")
    
    if not page_idx.isdecimal():
        return respond(ERR_WRONG_FORMAT, "页号不是正整数！")
    
    lowerbound = int(page_idx) * int(page_size) + 1
    upperbound = (int(page_idx) + 1) * int(page_size) + 1
    memes = Meme.query.filter(and_(Meme.meme_id >= lowerbound, Meme.meme_id < upperbound)).all()

    meme_list = []
    for meme in memes:
        meme_data = {
            "memeId" : meme.meme_id,
            "caption": meme.caption,
            "imageUrl" : meme.image_url,
            "uploadUsername" : User.query.filter(User.user_id==meme.user_id).first().username,
            "uploadTime" : meme.upload_time,
            "uploadUserId" : meme.user_id,
            "views" : meme.views,
            "likes" : meme.likes,
            "isBlock": meme.is_block,
            "tags":[{
                "tagId": tag.tag_id,
                "tagName": tag.name
            } for tag in Tag.query.join(MemeTag,
                and_(MemeTag.meme_id==meme.meme_id, MemeTag.tag_id==Tag.tag_id)).all()]
        }

        meme_list.append(meme_data)

    return respond(0, "查询成功", {"memes":meme_list})

@app.route("/api/meme-search", methods=['POST'])
@login_required
def meme_search():
    keywords = [k.strip() for k in request.form.get('keywords').split(' ')]

    candidate_memes = Meme.query.filter()

    for kw in keywords:
        candidate_memes = candidate_memes.filter(or_(Meme.caption.ilike(f'%{kw}%'), # kw in caption
                Tag.query.join(
                        MemeTag, and_(
                            MemeTag.meme_id==Meme.meme_id,
                            MemeTag.tag_id==Tag.tag_id,
                            Tag.name.ilike(f'%{kw}%') # kw in tag
                        )
                    ).exists()
                ))

    meme_list = []
    for meme in candidate_memes.all():
        meme_data = {
            "memeId" : meme.meme_id,
            "caption": meme.caption,
            "imageUrl" : meme.image_url,
            "uploadUsername" : User.query.filter(User.user_id==meme.user_id).first().username,
            "uploadTime" : meme.upload_time,
            "views" : meme.views,
            "likes" : meme.likes,
            "isBlock": meme.is_block,
            "tags":[{
                "tagId": tag.tag_id,
                "tagName": tag.name
            } for tag in Tag.query.join(MemeTag,
                and_(MemeTag.meme_id==meme.meme_id, MemeTag.tag_id==Tag.tag_id)).all()]
        }

        meme_list.append(meme_data)

    return respond(0, "查询成功", {"memes":meme_list})



@app.route("/api/meme-from-internet", methods=['POST'])
# @login_required
def meme_from_internet():
    _url = f'https://www.diydoutu.com/diy/biaoqing/{randint(1, 11751)}'
    response = requests.get(_url)
    
    soup = BeautifulSoup(response.content, 'lxml')
    img = soup.find_all('img', class_='lazyload')[0]

    src = img.get('src')
    filename = src.split('/')[-1]
    caption = img.get('alt').split(',')[0]
    tags = [a.get('href').split('/')[-1] for a in soup.find_all('a', class_='btn btn-sm btn-outline-secondary')]
    print(src, caption, tags)

    img_response = requests.get(src)
    response.raise_for_status()

    filepath = os.path.join(MEME_FOLDER, datetime.now().strftime("%Y%m%d%H%M%S") +\
                             "%04x." % randint(0,16**4) + filename.split('.')[-1])
    while os.path.exists(filepath):
        filepath = os.path.join(MEME_FOLDER, datetime.now().strftime("%Y%m%d%H%M%S") +\
                                 "%04x." % randint(0,16**4) + filename.split('.')[-1])
        
    with open(filepath, 'wb') as file:
        for chunk in img_response.iter_content(1024):  # 分块写入
            file.write(chunk)

    # print(filepath)
    # return respond(0, "查询成功", {"file":filepath})
    
    meme = Meme(
        user_id=1,
        caption=caption,
        image_url=filepath
    )
    db.session.add(meme)
    db.session.commit()

    if tags is not None:
        for tag_name in tags:
            tag = Tag.query.filter(Tag.name==tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.commit()
            memeTag = MemeTag(
                meme_id=meme.meme_id,
                tag_id=tag.tag_id
            )
            db.session.add(memeTag)

    add_img_to_index(image_path=meme.image_url, image_id=meme.meme_id)

    db.session.commit()

    return respond(0, "上传成功！", {"memeId": meme.meme_id})

@app.route("/api/meme-search-by-image", methods=['POST'])
@login_required
def meme_search_by_image():

    img = request.files.get('image') or None
    k = request.form.get('k') or None

    for r in check_null_params(图片=img, 搜索数量=k):
        return r
    
    # print(img)
    indices = search_similar_img(img, int(k))
    print(indices)
    # breakpoint()

    meme_list = []
    for meme_id in indices.tolist():
        meme = Meme.query.filter(Meme.meme_id==meme_id).first()
        if meme is None:
            continue
        meme_data = {
            "memeId" : meme.meme_id,
            "caption": meme.caption,
            "imageUrl" : meme.image_url,
            "uploadUsername" : User.query.filter(User.user_id==meme.user_id).first().username,
            "uploadTime" : meme.upload_time,
            "views" : meme.views,
            "likes" : meme.likes,
            "isBlock": meme.is_block,
            "tags":[{
                "tagId": tag.tag_id,
                "tagName": tag.name
            } for tag in Tag.query.join(MemeTag,
                and_(MemeTag.meme_id==meme.meme_id, MemeTag.tag_id==Tag.tag_id)).all()]
        }

        meme_list.append(meme_data)

    return respond(0, "查询成功", {"memes":meme_list})