import numpy as np
from PIL import Image
import cv2
# import copy


def color_range(color):
    c_range = 50
    r, g, b = color
    color = [b, g, r]
    return [i - (c_range if i > c_range else i) for i in color], \
           [(i + c_range) if i < 255 - c_range else 255 for i in color]


color = [
    color_range([255, 0, 0]),
    color_range([153, 43, 51]),
    color_range([0, 0, 153]),
    color_range([0, 128, 153]),
    color_range([255, 170, 0]),
    color_range([0, 0, 0]),
    color_range([0, 128, 0]),
]

scale = 4


def process_image(path):
    pic = Image.open(path).convert('RGB') \
        .crop((8, 5, 72, 21)).resize((66 * scale, 16 * scale), Image.ANTIALIAS)
    opencvImage = cv2.cvtColor(np.array(pic), cv2.COLOR_RGBA2BGR)
    pic.close()

    # clone_img = copy.copy(opencvImage)
    for (lower, upper) in color:
        # 创建NumPy数组
        lower = np.array(lower, dtype="uint8")  # 颜色下限
        upper = np.array(upper, dtype="uint8")  # 颜色上限

        # 根据阈值找到对应颜色
        mask = cv2.inRange(opencvImage, lower, upper)
        output = cv2.bitwise_and(opencvImage, opencvImage, mask=mask)

        # pix_sum = 0
        # projections = []
        # for col_count in range(len(mask[0])):
        #    projection = 0
        #    for pix_count in range(len(mask)):
        #        pix = mask[pix_count, col_count]
        #        pix_bin = pix and 1
        #        projection += pix_bin
        #        pix_sum += pix_bin
        #    projections.append(projection)
        #
        # if pix_sum < 100:
        #    continue
        #
        # split_by_threshold = []
        # threshold = 5
        #
        # curr = []
        # for idx, projection in enumerate(projections):
        #    if projection <= threshold:
        #        if len(curr) > 0:
        #            split_by_threshold.append(curr)
        #            curr = []
        #        continue
        #    curr.append((idx, projection))
        #
        # print(len(split_by_threshold))
        #
        # x = range(len(projections))
        # y = projections
        # plt.figure()
        # plt.plot(x, y)
        # plt.show()

        contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

        # cv2.imshow("images", np.hstack([opencvImage, output]))
        # cv2.imshow("mask", mask)
        # cv2.waitKey(5000)

        centers = []
        for cnt in contours[1]:
            # 得到最小矩形区域，转换为顶点坐标形式（矩形可能会有角度）
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            Xs = [i[0] for i in box]
            Ys = [i[1] for i in box]
            x1 = min(Xs)
            x2 = max(Xs)
            y1 = min(Ys)
            y2 = max(Ys)
            height = y2 - y1
            width = x2 - x1

            # 筛掉面积过小的区块
            square = height * width
            if square < 500:
                continue

            # cv2.rectangle(opencvImage, (x1, y1), (x2, y2), (255, 0, 0))
            # for i in range(len(box)):
            #    cv2.line(clone_img, tuple(box[i]), tuple(box[(i + 1) % 4]), (0, 0, 0))

            center = (x1 + x2) / 2
            if width <= 20 * scale:
                centers.append((center, square))
            else:
                dst = width / scale
                centers.append((center - dst, square))
                centers.append((center + dst, square))

        if len(centers) < 5:
            continue

        # print(centers)

        centers.sort(key=lambda x: float(x[0]))

        length = len(centers)
        last_item = centers[length - 1]
        for i in range(length - 2, -1, -1):
            current_item = centers[i]
            if abs(current_item[0] - last_item[0]) <= 5 * scale:
                if current_item[1] < last_item[1]:
                    centers.remove(current_item)
                else:
                    centers.remove(last_item)
                    last_item = current_item
            else:
                last_item = current_item

        # print(centers)
        if len(centers) < 5:
            continue

        images = []
        for center in centers:
            size = (16 * scale, 16 * scale)
            cropped = cv2.getRectSubPix(mask, size, (center[0], 8 * scale))
            ret, th = cv2.threshold(cropped, 100, 255, cv2.THRESH_BINARY)
            images.append(th)
            # cv2.imshow("mask", th)
            # cv2.waitKey(500)

        # cv2.imshow("mask", clone_img)
        # cv2.waitKey(1000)
        # clone_img = copy.copy(opencvImage)
        return images


# images = process_image('/media/ztc/折腾/checkcode/checkcode_files/CheckCode(1).gif')
try:
    fail_list = open("./CheckCode/failCrop.list", 'w+')
    for i in range(1000):
        path = './CheckCode/checkcode_files/CheckCode(%d).gif' % i
        images = process_image(path)
        if images is None or len(images) != 5:
            fail_list.writelines(str(i)+'\n')
            print(i)
            continue
        for j, im in enumerate(images):
            out = './CheckCode/checkcode_bin/%04d_%d.png' % (i, j)
            cv2.imwrite(out, im)
finally:
    fail_list.close()