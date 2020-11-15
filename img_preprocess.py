from PIL import Image
import numpy as np
import os
import cv2
import random
from matplotlib import pyplot as plt

def laplace_sharpen(input_image, c):
    '''
    拉普拉斯锐化
    :param input_image: 输入图像
    :param c: 锐化系数
    :return: 输出图像
    '''
    input_image_cp = np.copy(input_image)  # 输入图像的副本

    # 拉普拉斯滤波器
    laplace_filter = np.array([
        [1, 1, 1],
        [1, -8, 1],
        [1, 1, 1],
    ])

    input_image_cp = np.pad(input_image_cp, (1, 1), mode='constant', constant_values=0)  # 填充输入图像

    m, n = input_image_cp.shape  # 填充后的输入图像的尺寸

    output_image = np.copy(input_image_cp)  # 输出图像

    for i in range(1, m - 1):
        for j in range(1, n - 1):
            R = np.sum(laplace_filter * input_image_cp[i - 1:i + 2, j - 1:j + 2])  # 拉普拉斯滤波器响应

            output_image[i, j] = input_image_cp[i, j] + c * R

    output_image = output_image[1:m - 1, 1:n - 1]  # 裁剪
    return output_image


def adaptive_threshold(gray, blockSize=5, C=10, inv=False):
    if inv == False:
        thresholdType = cv2.THRESH_BINARY
    else:
        thresholdType = cv2.THRESH_BINARY_INV
    # 自适应阈值化能够根据图像不同区域亮度分布，改变阈值
    binary_img = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, thresholdType, blockSize, C)
    return binary_img

# show shuiping he chuizhi
def get_projection_list_demo(binary_img):
    h, w = binary_img.shape[:2]
    row_list = [0] * h
    col_list = [0] * w
    for row in range(h):
        for col in range(w):
            if binary_img[row, col] == 0:
                row_list[row] = row_list[row] + 1
                col_list[col] = col_list[col] + 1

    # 显示水平投影
    temp_img_1 = 255 - np.zeros((binary_img.shape[0], max(row_list)))
    for row in range(h):
        for i in range(row_list[row]):
            temp_img_1[row, i] = 0
    cv2.imshow('horizontal', temp_img_1)

    # 显示垂直投影
    temp_img_2 = 255 - np.zeros((max(col_list), binary_img.shape[1]))
    for col in range(w):
        for i in range(col_list[col]):
            temp_img_2[i, col] = 0
    cv2.imshow('vertical', temp_img_2)
    cv2.waitKey()

# fanhui liantongkuai de qizhi weizhi
def split_projection_list(projectionList: list, minValue=0):
    start = 0
    end = None

    split_list = []
    for idx, value in enumerate(projectionList):
        if value > minValue:
            end = idx
        else:
            if end is not None:
                split_list.append((start, end))
                end = None
            start = idx
    # else:
    #     if end is not None:
    #         split_list.append((start, end))
    #         end = None
    return split_list


def get_projection_list(binary_img, direction='horizontal'):
    h, w = binary_img.shape[:2]
    row_list = [0] * h
    col_list = [0] * w
    for row in range(h):
        for col in range(w):
            if binary_img[row, col] == 0:
                row_list[row] = row_list[row] + 1
                col_list[col] = col_list[col] + 1
    if direction == 'horizontal':
        return row_list
    else:
        return col_list


def cut_binary_img(binary_img, direction='horizontal', iteration=2):
    img_h, img_w = binary_img.shape[:2]
    if iteration <= 0:
        return

    projection_list = get_projection_list(binary_img, direction)
    split_list = split_projection_list(projection_list, minValue=2)
    for start, end in split_list:
        if end - start < 5:  # 过滤虚线框
            continue
        if direction == 'horizontal':
            x, y, w, h = 0, start, img_w, end - start
        else:
            x, y, w, h = start, 0, end - start, img_h

        roi = binary_img[y:y + h, x:x + w]
        if direction == 'horizontal':
            next_direction = 'vertical'
        else:
            next_direction = 'horizontal'
        cut_binary_img(roi, next_direction, iteration - 1)


def cut_binary_img1(binary_img, startX, startY, direction='horizontal', iteration=2):
    img_h, img_w = binary_img.shape[:2]
    if iteration <= 0:
        return {
            'rect': (startX, startY, img_w, img_h),
            'childern': None
        }

    children = []

    projection_list = get_projection_list(binary_img, direction)
    minValue = int(0.1 * sum(projection_list) / len(projection_list))
    # minValue = 2
    split_list = split_projection_list(projection_list, minValue)
    for start, end in split_list:
        if end - start < 5:
            continue
        if direction == 'horizontal':
            x, y, w, h = 0, start, img_w, end - start
        else:
            x, y, w, h = start, 0, end - start, img_h

        roi = binary_img[y:y + h, x:x + w]
        if direction == 'horizontal':
            next_direction = 'vertical'
        else:
            next_direction = 'horizontal'
        grandchildren = cut_binary_img1(roi, startX + x, startY + y, next_direction, iteration - 1)

        children.append(grandchildren)

    root = {
        'rect': (startX, startY, img_w, img_h),
        'childern': children
    }
    return root


def get_leaf_node(root):
    leaf_rects = []
    if root['childern'] is None:
        leaf_rect = root['rect']
        leaf_rects.append(leaf_rect)
    else:
        for childern in root['childern']:
            rects = get_leaf_node(childern)
            leaf_rects.extend(rects)
    return leaf_rects


def draw_rects(img, rects):
    new_img = img.copy()
    for x, y, w, h in rects:
        p1 = (x, y)
        p2 = (x + w, y + h)

        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # color = (0, 0, 255)
        cv2.rectangle(new_img, p1, p2, color, 2)
    return new_img