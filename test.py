# -*- coding: utf-8 -*-
import urllib.request, http.cookiejar, urllib
from PIL import Image
from bs4 import BeautifulSoup
import numpy as np
import cv2
from keras.models import *
import string


# 用户信息
username = ''
password = ''

# 携带Cookie获取验证码并保留在CookieJar中管理
# captcha_url = "http://jwgl3.jmu.edu.cn/Common/CheckCode.aspx"
# cookie = http.cookiejar.CookieJar()
# opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie), urllib.request.HTTPHandler)
# urllib.request.install_opener(opener)
# captcha = opener.open(captcha_url).read()
# try:
    # local = open('./captcha.gif', 'wb')
    # local.write(captcha)
# finally:
    # local.close()

def color_range(color):
    c_range = 50
    r, g, b = color
    color = [b, g, r]
    return np.clip([i - c_range for i in color], 0, 255), \
           np.clip([i + c_range for i in color], 0, 255)


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
    cv_image = cv2.cvtColor(np.array(code_pic), cv2.COLOR_RGB2BGR)
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


characters = string.digits


def vec2word(vec):
    char_idxs = np.argmax(vec, axis=1)
    return ''.join([characters[idx] for idx in char_idxs])


model = load_model('jmu_jw_captcha_break_splited.h5')
width, height = 12, 16

images_path = "./captcha.gif"
images = process_image(images_path)
X = np.zeros((len(images), height, width, 1), dtype=np.uint8)
for idx, im in enumerate(images):
X[idx, :, :, 0] = im[:, :]
y = model.predict(X)
predict_word = vec2word(y)
print(predict_word)
# os.system("pause")