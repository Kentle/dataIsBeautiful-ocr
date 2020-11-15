import argparse
# import pytesseract
from PIL import Image
import numpy as np
import os
import cv2
import random
import ocr
import re
import xlwt
import copy
from matplotlib import pyplot as plt
from utils import wt_xls
import img_preprocess as ip
# pytesseract.pytesseract.tesseract_cmd = 'D:/TesseractOCR/Tesseract-OCR/tesseract.exe'
# tessdata_dir_config = '--tessdata-dir "D:/TesseractOCR/Tesseract-OCR/tessdata"'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-video', type=str, default='./videos/browsers.mp4')
    parser.add_argument('-output_dir', type=str, default='./result')
    parser.add_argument('-save_tmp', type=int, default=1)
    args = parser.parse_args()
    print(args)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # 读取视频截取图片
    select_pictures(args.video, args.output_dir)
    # 结果存到 args.output_dir + "/pictures/"
    #####################

    res_list = []
    img_path = args.output_dir + "/pictures/"
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    img_dirs = os.listdir(img_path)
    for file in img_dirs:
        print("===== processing: ", file," =====")
        reader = ocr.Reader(lang_list=["en"], gpu=True)
        raw_image = cv2.imread(img_path + file)
        # raw_image = cv2.imread(img_path + "2011_Q3.jpg")
        new_img = raw_image.copy()
        # 颜色过滤
        for m in range(new_img.shape[0]):
            for n in range(new_img.shape[1]):
                tmp_px = new_img[m, n, :]
                if ((tmp_px[0] < 60) and (tmp_px[1] < 60) and (tmp_px[2] < 60)):
                    pass
                else:
                    new_img[m, n, :] = [255, 255, 255]
        # 高斯滤波
        blurred = cv2.GaussianBlur(new_img, (3, 3), 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        # 二值化
        binary_img = ip.adaptive_threshold(gray, blockSize=15)

        # 文字检测 free_list没什么用
        horizontal_list, free_list = reader.detectonly(binary_img, detail=1)
        index = 0
        nlist = []  # name
        rlist = []  # rate
        tmp_list = horizontal_list[:]  # 浅拷贝
        for i in range(len(horizontal_list)):
            for j in range(len(horizontal_list)):
                if i >= j:
                    continue
                # 对连在一起却被检测为两个词的情况做合并
                if (abs(horizontal_list[i][2]-horizontal_list[j][2]) < 20 and \
                        abs(horizontal_list[i][3]-horizontal_list[j][3]) < 20 and \
                        abs(horizontal_list[i][1] - horizontal_list[j][0]) < 20 ):
                    tmp_list[tmp_list.index(horizontal_list[j])] = \
                    [horizontal_list[i][0],horizontal_list[j][1],horizontal_list[i][2],horizontal_list[j][3]]
                    tmp_list.remove(horizontal_list[i])

        horizontal_list = tmp_list
        for rect in horizontal_list:
            # 增大识别的范围
            horizontal_list[index][0] = rect[0]-5
            horizontal_list[index][1] = rect[1]+7
            horizontal_list[index][2] = rect[2]-5
            horizontal_list[index][3] = rect[3]+5
            index = index + 1
            if args.save_tmp:
                p1 = (rect[0]-5, rect[2]-5)
                p2 = (rect[1]+7, rect[3]+5)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                # color = (0, 0, 255)
                cv2.rectangle(raw_image, p1, p2, color, 2)
        if args.save_tmp:
            # 将中间过程保存
            save_dir = args.output_dir + '/tmp_result/'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            cv2.imwrite(save_dir + file, raw_image)

        result = reader.recogonly(raw_image, horizontal_list, free_list,detail=0)
        for word in result:
            # 过滤掉过短的无意义字符串
            if len(word) < 4:
                continue

            # 如果是数字，加到rlist
            if word.find('.') >= 0:
                tmpword = re.sub("[^0-9.]","",word)
                rlist.append(tmpword)
            # 如果是字母，加到nlist
            else:
                tmpword = re.sub("[^a-zA-Z\s]", "", word)
                if tmpword.find("Navigator") >= 0:
                    tmpword = "Netscape Navigator" # 对猫头鹰的特殊处理
                nlist.append(tmpword)
        tmp_dict = {"name":file[:-4]}
        for i in range(len(nlist)):
            tmp_dict[nlist[i]] = round(float(rlist[i])/100.,4)  # 保留四位小数
        print(tmp_dict)
        res_list.append(tmp_dict)
        # break

    wt_xls(res_list,args.output_dir + '/sheet.xls')  # 存取识别结果到表格

    # 此处完成了OCR识别，接下来完成后续的可视化
