import io
import json
import os
import glob
from random import randint
from turtle import down
from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from scripts.init import app

post_url = ""

def download_image(image_url, save_path):
    # 检查文件夹是否存在，如果不存在则创建
    # if not os.path.exists(os.path.dirname(save_path)):
    #     os.makedirs(os.path.dirname(save_path))

    # 设置 Chrome 的选项，避免弹出窗口并模拟正常的浏览器行为
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU
    chrome_options.add_argument("--no-sandbox")  # 在 Linux 系统下，避免一些沙箱错误
    chrome_options.add_argument("start-maximized")

    # 指定 ChromeDriver 路径
    # s = Service("path_to_chromedriver")  # 请替换为你自己的 ChromeDriver 路径

    # 启动浏览器
    driver = webdriver.Chrome(options=chrome_options)

    # 访问图片 URL
    driver.get(image_url)
    driver.get_screenshot_as_file('s.png')
    breakpoint()
    # 获取图片的 src 地址
    img_element = driver.find_element("tag name", "img")  # 假设页面中只有一张图片
    img_src = img_element.get_attribute("src")

    # 关闭浏览器
    driver.quit()


def find_filename(path, filename):
    pattern = os.path.join(path, f"{filename}.*")  # Match any extension
    files = glob.glob(pattern)
    return files[0] if files else None

def test():
    global post_url
    post_url = f"http://127.0.0.1:{app.config['PORT']}"

    session = requests.Session()
    # test_from_internet(session)
    # return

    test_create_user(session)
    
    test_meme(session)

    test_interact(session)

    test_bookmark(session)

    test_admin(session)

    test_message(session)


def test_from_internet(session: requests.Session, times=100):
    for i in range(times):
        result = session.post(f'{post_url}/api/meme-from-internet')
        print('fetch', i)
    print(json2txt(result.text))

def json2txt(json_text:str):
    if not json_text.startswith("{") :
        return json_text
    return json.dumps(json.loads(json_text), ensure_ascii=False, indent=4)



def do_login(session: requests.Session, username, passwd):
    form_data = {
        'username':username,
        'password': passwd,
    }
    result = session.post(f'{post_url}/api/auth-login',data=form_data)
    session.headers['Cookie'] = result.headers.get('Set-Cookie')
    return json2txt(result.text)



def test_create_user(session: requests.Session):
    form_data = {
        'username':"cxc",
        'email': "a@b.cd",
        'password': "abc",
    }
    result = session.post(f'{post_url}/api/auth-signup',data=form_data)
    print(json2txt(result.text))

    form_data = {
        'username':"cxc2",
        'email': "a@b.cde",
        'password': "abcd",
    }
    result = session.post(f'{post_url}/api/auth-signup',data=form_data)
    print(json2txt(result.text))

    print(do_login(session, "cxc", "abc"))

    avatar = open('./static/default.jpg', 'rb')
    result = session.post(f'{post_url}/api/userinfo-update-avatar', files={'avatar':avatar})
    print(json2txt(result.text))

    bio = "Man! what can I say? Database out!"
    form_data = {
        'bio':bio,
    }
    result = session.post(f'{post_url}/api/userinfo-update-bio',data=form_data)
    print(json2txt(result.text))

    
    result = session.post(f'{post_url}/api/userinfo-get-current-user')
    print(json2txt(result.text))



def test_meme(session: requests.Session):
    for i in range(1,10+1):
        file = open(find_filename(f'./static/assets', f'm{i}'), 'rb')
        form_data = {
            'caption': f"猫{i}",
            'tags': "猫; 可爱; 写实"
        }
        result = session.post(f'{post_url}/api/meme-upload', data=form_data, files={'meme':file})
    
    print(json2txt(result.text))

    for i in range(1,10+1):

        file = open(find_filename(f'./static/assets', f'nl{i}'), 'rb')
        form_data = {
            'caption': f"奶龙{i}",
            'tags': "奶龙; 动画; 抽象;"
        }
        result = session.post(f'{post_url}/api/meme-upload', data=form_data, files={'meme':file})
    
    print(json2txt(result.text))

    form_data = {
        'content': "无内鬼，来张龙图",
        'bounty': 3
    }
    result = session.post(f'{post_url}/api/post-create',data=form_data)
    print(json2txt(result.text))



def test_interact(session: requests.Session):
    form_data = {
        'userId': "3",
    }
    result = session.post(f'{post_url}/api/follow-add',data=form_data)
    print(json2txt(result.text))

    print(do_login(session, "cxc2", "abcd"))

    form_data = {
        'userId': "2",
    }
    result = session.post(f'{post_url}/api/follow-add',data=form_data)
    print(json2txt(result.text))

    form_data = {
        'memeId': "1",
        'content': "what a meme",
        'toCommentId': "",
    }
    result = session.post(f'{post_url}/api/comment-add',data=form_data)

    form_data = {
        'memeId': "1",
        'content': "comment to what a meme",
        'toCommentId': "1",
    }
    result = session.post(f'{post_url}/api/comment-add',data=form_data)
    
    print(json2txt(result.text))

    form_data = {
        'memeId': "1",
    }
    result = session.post(f'{post_url}/api/like-add',data=form_data)
    form_data = {
        'memeId': "1",
    }
    result = session.post(f'{post_url}/api/like-add',data=form_data)
    
    print(json2txt(result.text))

    from scripts.config import WIN
    file = open('.\\static\\default.jpg', 'rb') if WIN else open('./static/default.jpg', 'rb')
    form_data = {
        'caption': "is it 龙图？",
        'tags': "loong",
        'postId':1
    }
    result = session.post(f'{post_url}/api/meme-upload',data=form_data, files={'meme':file})
    
    print(json2txt(result.text))


def test_bookmark(session: requests.Session):
    print(do_login(session, "cxc", "abc"))

    form_data = {
        'name': 'myWarehouse'
    }
    result = session.post(f'{post_url}/api/warehouse-create', data=form_data)
    print(json2txt(result.text))

    form_data = {
        'memeId': '3',
        'warehouseId': '1',
    }
    result = session.post(f'{post_url}/api/warehouse-add-bookmark', data=form_data)
    form_data = {
        'memeId': '5',
        'warehouseId': '1',
    }
    result = session.post(f'{post_url}/api/warehouse-add-bookmark', data=form_data)
    print(json2txt(result.text))

def test_admin(session: requests.Session):
    print(do_login(session, "cxc2", "abcd"))
    form_data = {
        'memeId': '5',
        'reason': 'ju ban le'
    }
    result = session.post(f'{post_url}/api/report-issue', data=form_data)
    print(json2txt(result.text))

    print(do_login(session, "admin", "root"))

    form_data = {
        'reportId': '1',
    }
    result = session.post(f'{post_url}/api/admin-deal-with-report', data=form_data)
    print(json2txt(result.text))

    form_data = {
        'userId': '2',
    }
    result = session.post(f'{post_url}/api/admin-block-user', data=form_data)
    print(json2txt(result.text))
    result = session.post(f'{post_url}/api/admin-unblock-user', data=form_data)
    print(json2txt(result.text))

    form_data = {
        'memeId': '4',
    }
    result = session.post(f'{post_url}/api/admin-block-meme', data=form_data)
    print(json2txt(result.text))
    result = session.post(f'{post_url}/api/admin-unblock-meme', data=form_data)
    print(json2txt(result.text))


def test_message(session: requests.Session):
    print(do_login(session, "cxc", "abc"))
    result = session.post(f'{post_url}/api/message-get-user-unread-message')
    print(json2txt(result.text))

    print(do_login(session, "cxc2", "abcd"))
    result = session.post(f'{post_url}/api/message-get-user-unread-message')
    print(json2txt(result.text))


if __name__ == "__main__":
    test()