# -*- coding: utf-8 -*-
import urllib.request, http.cookiejar, urllib
from PIL import Image
from bs4 import BeautifulSoup
import numpy as np
import cv2


# home_url = "http://jwgls.jmu.edu.cn/Login.aspx"
# home_page = BeautifulSoup(urllib.request.urlopen(home_url), "html.parser", from_encoding="gb2312")
# get_viewstate = (home_page.find_all("input", id="__VIEWSTATE")[0])["value"]

# 用户信息
username = ''
password = ''

# 携带Cookie获取验证码并保留在CookieJar中管理
captcha_url = "http://jwgls.jmu.edu.cn/Common/CheckCode.aspx"
cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie), urllib.request.HTTPHandler)
urllib.request.install_opener(opener)
captcha = opener.open(captcha_url).read()


def color_range(color):
    c_range = 50
    r, g, b = color
    color = [b, g, r]
    return [i - (c_range if i > c_range else i) for i in color], \
           [(i + c_range) if i < 255 - c_range else 255 for i in color]


colors = [
    color_range([255, 0, 0]),
    color_range([153, 43, 51]),
    color_range([204, 43, 51]),
    color_range([0, 0, 153]),
    color_range([0, 0, 102]),
    color_range([0, 128, 153]),
    color_range([0, 170, 153]),
    color_range([255, 170, 0]),
    color_range([255, 128, 0]),
    color_range([0, 0, 0]),
    color_range([0, 128, 0]),
    color_range([0, 85, 0])
]


def process_image(path):
    code_pic = Image.open(path).convert('RGB').crop((8, 5, 72, 21))
    cv_image = cv2.cvtColor(np.array(code_pic), cv2.COLOR_RGBA2BGR)
    pics = []
    center = [6, 18, 30, 42, 54]
    for (lower, upper) in colors:
        # 创建NumPy数组
        lower = np.array(lower, dtype="uint8")  # 颜色下限
        upper = np.array(upper, dtype="uint8")  # 颜色上限

        # 根据阈值找到对应颜色
        mask = cv2.inRange(cv_image, lower, upper)
        if np.sum(mask) > 14000:
            break
    for a in range(5):
        size = (12, 16)
        cropped = cv2.getRectSubPix(mask, size, (center[a], 8))
        pics.append(cropped)
    return pics


width, height = 12, 16
images_path = 'captcha.gif'
images = process_image(images_path)
for j in range(len(images)):
    # out = 'captcha_bin/captcha_%d.png' % j
    # cv2.imwrite(out, images[j])
    X = np.zeros((len(images_path), height, width, 1), dtype=np.uint8)
    for idx, path in enumerate(images_path):
        pic = Image.open(path)
        pix = np.array(pic)
        pic.close()
        X[idx, :, :, 0] = pix[:, :]



# local = open('./captcha.tif', 'wb')
# local.write(captcha)
# local.close()
# img = Image.open("./captcha.tif")
# img.show()
# CheckCode = input('输入验证码： ')

exit()
# 创建post数据
post_data = urllib.parse.urlencode({
    '__VIEWSTATE': get_viewstate,
    'TxtUserName': username,
    'TxtPassword': password,
    'TxtVerifCode': CheckCode,
    'BtnLoginImage.x': '0',
    'BtnLoginImage.y': '0'
})
post_data = post_data.encode('utf-8')

# 创建header数据，禁止gzip压缩，防止解码问题
headers = dict({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'http://jwgls.jmu.edu.cn/Login.aspx',
    'Connection': 'Keep-Alive'
})

# 构建请求，模拟登录post
login_request = urllib.request.Request(home_url, data=post_data, headers=headers)
login_response = urllib.request.urlopen(login_request)
login_status = login_response.read()

# 解析post后页面，判断是否登录
login_page = BeautifulSoup(login_status, "html.parser")
get_title = str(login_page.find_all("title")[0].get_text(strip=True))
if get_title == "集美大学综合教务管理系统":
    print("You Are Now Logged In !!!")
    flag = 1
else:
    print("Log In FAILED.")
    print("Please Retry to Log In.")
    flag = 0

# 登录后执行抓取课表，进行解析
if flag == 1:
    print("Getting Your Classes...")
    class_html = "http://jwgls.jmu.edu.cn/Student/ViewMyStuSchedule.aspx"
    class_request = urllib.request.Request(class_html, headers=headers)
    class_response = urllib.request.urlopen(class_request)
    class_status = class_response.read()
    class_page = BeautifulSoup(class_status, "html.parser", from_encoding="utf-8")
    class_page.tr.clear()
    class_output = class_page.prettify().replace("&nbsp;","")
    class_html = open("./Classes.html", "w", encoding='utf-8')
    print(class_output, file=class_html)
    class_html.close()
    print("Classes.html is place in the folder, plz open it.")