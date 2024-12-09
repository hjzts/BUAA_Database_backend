import io
import json
import requests


def test():
    session = requests.Session()

    test_create_user(session)
    
    test_meme(session)

    test_interact(session)

    test_bookmark(session)

    test_admin(session)

    test_message(session)

def json2txt(json_text:str):
    if not json_text.startswith("{") :
        return json_text
    return json.dumps(json.loads(json_text), ensure_ascii=False, indent=4)



def do_login(session: requests.Session, username, passwd):
    form_data = {
        'username':username,
        'password': passwd,
    }
    result = session.post('http://127.0.0.1:5000/api/auth-login',data=form_data)
    session.headers['Cookie'] = result.headers.get('Set-Cookie')
    return json2txt(result.text)



def test_create_user(session: requests.Session):
    form_data = {
        'username':"cxc",
        'email': "a@b.cd",
        'password': "abc",
    }
    result = session.post('http://127.0.0.1:5000/api/auth-signup',data=form_data)
    print(json2txt(result.text))

    form_data = {
        'username':"cxc2",
        'email': "a@b.cde",
        'password': "abcd",
    }
    result = session.post('http://127.0.0.1:5000/api/auth-signup',data=form_data)
    print(json2txt(result.text))

    print(do_login(session, "cxc", "abc"))

    avatar = open('./static/default.jpg', 'rb')
    result = session.post('http://127.0.0.1:5000/api/userinfo-update-avatar', files={'avatar':avatar})
    print(json2txt(result.text))

    bio = "Man! what can I say? Database out!"
    form_data = {
        'bio':bio,
    }
    result = session.post('http://127.0.0.1:5000/api/userinfo-update-bio',data=form_data)
    print(json2txt(result.text))

    
    result = session.post('http://127.0.0.1:5000/api/userinfo-get-current-user')
    print(json2txt(result.text))



def test_meme(session: requests.Session):
    file = open('./static/default.jpg', 'rb')
    form_data = {
        'caption': "a meme1",
        'tags': "114; 514; mamba out1"
    }
    result = session.post('http://127.0.0.1:5000/api/meme-upload',data=form_data, files={'meme':file})

    form_data = {
        'caption': "a meme2",
        'tags': "114; 514; mamba out2"
    }
    result = session.post('http://127.0.0.1:5000/api/meme-upload',data=form_data, files={'meme':file})

    form_data = {
        'caption': "a meme3",
        'tags': "114; 514; mamba out3"
    }
    result = session.post('http://127.0.0.1:5000/api/meme-upload',data=form_data, files={'meme':file})

    form_data = {
        'caption': "a meme4",
        'tags': "114; 514; mamba out4"
    }
    result = session.post('http://127.0.0.1:5000/api/meme-upload',data=form_data, files={'meme':file})

    form_data = {
        'caption': "a meme5",
        'tags': "114; 514; mamba out5"
    }
    result = session.post('http://127.0.0.1:5000/api/meme-upload',data=form_data, files={'meme':file})
    
    print(json2txt(result.text))

    form_data = {
        'content': "无内鬼，来张龙图",
        'bounty': 3
    }
    result = session.post('http://127.0.0.1:5000/api/post-create',data=form_data)
    print(json2txt(result.text))



def test_interact(session: requests.Session):
    form_data = {
        'userId': "3",
    }
    result = session.post('http://127.0.0.1:5000/api/follow-add',data=form_data)
    print(json2txt(result.text))

    print(do_login(session, "cxc2", "abcd"))

    form_data = {
        'userId': "2",
    }
    result = session.post('http://127.0.0.1:5000/api/follow-add',data=form_data)
    print(json2txt(result.text))

    form_data = {
        'memeId': "1",
        'content': "what a meme",
        'toCommentId': "",
    }
    result = session.post('http://127.0.0.1:5000/api/comment-add',data=form_data)

    form_data = {
        'memeId': "1",
        'content': "comment to what a meme",
        'toCommentId': "1",
    }
    result = session.post('http://127.0.0.1:5000/api/comment-add',data=form_data)
    
    print(json2txt(result.text))

    form_data = {
        'memeId': "1",
    }
    result = session.post('http://127.0.0.1:5000/api/like-add',data=form_data)
    form_data = {
        'memeId': "1",
    }
    result = session.post('http://127.0.0.1:5000/api/like-add',data=form_data)
    
    print(json2txt(result.text))

    file = open('./static/default.jpg', 'rb')
    form_data = {
        'caption': "is it 龙图？",
        'tags': "loong",
        'postId':1
    }
    result = session.post('http://127.0.0.1:5000/api/meme-upload',data=form_data, files={'meme':file})
    
    print(json2txt(result.text))


def test_bookmark(session: requests.Session):
    print(do_login(session, "cxc", "abc"))

    form_data = {
        'name': 'myWarehouse'
    }
    result = session.post('http://127.0.0.1:5000/api/warehouse-create', data=form_data)
    print(json2txt(result.text))

    form_data = {
        'memeId': '3',
        'warehouseId': '1',
    }
    result = session.post('http://127.0.0.1:5000/api/warehouse-add-bookmark', data=form_data)
    form_data = {
        'memeId': '5',
        'warehouseId': '1',
    }
    result = session.post('http://127.0.0.1:5000/api/warehouse-add-bookmark', data=form_data)
    print(json2txt(result.text))

def test_admin(session: requests.Session):
    print(do_login(session, "cxc2", "abcd"))
    form_data = {
        'memeId': '5',
        'reason': 'ju ban le'
    }
    result = session.post('http://127.0.0.1:5000/api/report-issue', data=form_data)
    print(json2txt(result.text))

    print(do_login(session, "admin", "root"))

    form_data = {
        'reportId': '1',
    }
    result = session.post('http://127.0.0.1:5000/api/admin-deal-with-report', data=form_data)
    print(json2txt(result.text))

    form_data = {
        'userId': '2',
    }
    result = session.post('http://127.0.0.1:5000/api/admin-block-user', data=form_data)
    print(json2txt(result.text))
    result = session.post('http://127.0.0.1:5000/api/admin-unblock-user', data=form_data)
    print(json2txt(result.text))

    form_data = {
        'memeId': '4',
    }
    result = session.post('http://127.0.0.1:5000/api/admin-block-meme', data=form_data)
    print(json2txt(result.text))
    result = session.post('http://127.0.0.1:5000/api/admin-unblock-meme', data=form_data)
    print(json2txt(result.text))



def test_message(session: requests.Session):
    print(do_login(session, "cxc", "abc"))
    result = session.post('http://127.0.0.1:5000/api/message-get-user-unread-message')
    print(json2txt(result.text))

    print(do_login(session, "cxc2", "abcd"))
    result = session.post('http://127.0.0.1:5000/api/message-get-user-unread-message')
    print(json2txt(result.text))

if __name__ == "__main__":
    test()