from PIL import Image
import cv2
import numpy as np


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


for j in range(1000):
    images_path = "CheckCode/checkcode_files/CheckCode(%d).gif" % j
    images = process_image(images_path)
    for k in range(len(images)):
        out = 'CheckCode/checkcode_bin/%04d_%d.png' % (j, k)
        cv2.imwrite(out, images[k])
