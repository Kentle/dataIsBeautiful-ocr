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
from utils import wt_xls,select_pictures
import img_preprocess as ip
# pytesseract.pytesseract.tesseract_cmd = 'D:/TesseractOCR/Tesseract-OCR/tesseract.exe'
# tessdata_dir_config = '--tessdata-dir "D:/TesseractOCR/Tesseract-OCR/tessdata"'

DBG_OCR = False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-video', type=str, default='./videos/Programming Languages.mp4')
    parser.add_argument('-output_dir', type=str, default='./result')
    parser.add_argument('-save_tmp', type=int, default=1)
    args = parser.parse_args()
    print(args)
    video_name = args.video.split('/')[-1][:-4]
    output_dir = args.output_dir + "/" + video_name
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    img_path = output_dir + "/pictures/"
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    # 读取视频截取图片
    # select_pictures(args.video, output_dir)
    print("Pictures Selected Successfully.")
    # exit(0)
    res_list = []
    img_dirs = os.listdir(img_path)
    for file in img_dirs:
        print("===== processing: ", file," =====")
        reader = ocr.Reader(lang_list=["en"], gpu=True)
        raw_image = cv2.imread(img_path + file)
        # raw_image = cv2.imread(img_path + "2002_Q2.jpg")
        new_img = raw_image.copy()
        # 颜色过滤

        for m in range(new_img.shape[0]):
            for n in range(new_img.shape[1]):
                tmp_px = new_img[m, n, :]
                if (tmp_px[0] < 60) \
                    and (tmp_px[1] < 60) \
                    and (tmp_px[2] < 60) \
                    and (abs(int(tmp_px[0]) - int(tmp_px[1])) < 10) \
                    and (abs(int(tmp_px[2]) - int(tmp_px[1])) < 10):
                    pass
                else:
                    new_img[m, n, :] = [255, 255, 255]

                if n >= 800 and n <= 1250 and m >= 550 and m <= 700:
                    new_img[m, n, :] = [255, 255, 255]



        # 高斯滤波
        blurred = cv2.GaussianBlur(new_img, (3, 3), 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        # 二值化
        binary_img = ip.adaptive_threshold(gray, blockSize=15)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
        erode_img = cv2.erode(binary_img, kernel)
        # ip.get_projection_list_demo(erode_img) # 画出投影
        # cv2.imshow("erode_img",erode_img)
        if args.save_tmp:
            # 将中间过程保存
            erode_dir = output_dir + '/erode/'
            if not os.path.exists(erode_dir):
                os.makedirs(erode_dir)
            cv2.imwrite(erode_dir + file, erode_img)
        H = 'horizontal'
        V = 'vertical'
        root = ip.cut_binary_img1(erode_img, 0, 0, direction=H, iteration=2)
        rects = ip.get_leaf_node(root)
        if DBG_OCR:
            print(rects)
        # new_img = ip.draw_rects(raw_image, rects)
        horizontal_list = []
        for x, y, w, h in rects:
            p1 = (x, y)
            p2 = (x + w, y + h)
            horizontal_list.append([p1[0],p2[0],p1[1],p2[1]])
        # get_projection_list_demo(binary_img)

        tmp_list = horizontal_list[:]  # 浅拷贝
        for i in range(len(horizontal_list)):
            for j in range(len(horizontal_list)):
                if i == j:
                    continue
                # 对连在一起却被检测为两个词的情况做合并
                if (horizontal_list[i][0] < horizontal_list[j][0] and
                        abs(horizontal_list[i][2] - horizontal_list[j][2]) < 20 and
                        abs(horizontal_list[i][3] - horizontal_list[j][3]) < 20 and
                        abs(horizontal_list[i][1] - horizontal_list[j][0]) < 20):
                    tmp_list[tmp_list.index(horizontal_list[j])] = \
                        [horizontal_list[i][0], horizontal_list[j][1], horizontal_list[i][2], horizontal_list[j][3]]
                    if horizontal_list[i] in tmp_list:
                        tmp_list.remove(horizontal_list[i])

                # 过滤掉比较小的框（干扰像素点）
                if (abs(horizontal_list[i][0] - horizontal_list[i][1]) < 25 and
                        abs(horizontal_list[i][2] - horizontal_list[i][3]) < 25):
                    if horizontal_list[i] in tmp_list:
                        tmp_list.remove(horizontal_list[i])

        if DBG_OCR:
            print(tmp_list)
        horizontal_list = tmp_list

        index = 0
        nlist = []  # name
        rlist = []  # rate
        if DBG_OCR:
            print(horizontal_list)
        rect_img = raw_image.copy()
        for rect in horizontal_list:
            # 增大识别的范围
            horizontal_list[index][0] = rect[0]-5
            horizontal_list[index][1] = rect[1]+7
            horizontal_list[index][2] = rect[2]-7
            horizontal_list[index][3] = rect[3]+7
            index = index + 1
            if args.save_tmp:
                p1 = (rect[0]-5, rect[2]-5)
                p2 = (rect[1]+5, rect[3]+5)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                cv2.rectangle(rect_img, p1, p2, color, 2)
        if args.save_tmp:
            # 将中间过程保存
            save_dir = output_dir + '/detect/'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            cv2.imwrite(save_dir + file, rect_img)
        result = reader.recogonly(raw_image, horizontal_list, [],detail=0)
        for word in result:
            # 如果是数字，加到rlist
            if word.find('.') >=0 or word.find(',') >= 0 or re.match("[0-9]",word):
                tmpword = re.sub("[^0-9.]","",word)
                # tmpword = re.sub("[^0-9]", "", word)
                if len(tmpword) < 1:
                    continue
                rlist.append(tmpword)
            # 如果是字母，加到nlist
            else:
                tmpword = re.sub("[^a-zA-Z\s+#]", "", word)
                if tmpword.find("Navigator") >= 0:
                    tmpword = "Netscape Navigator" # 对猫头鹰的特殊处理
                if tmpword.find("HUA") >= 0:
                    continue
                if len(tmpword) < 1:
                    continue
                nlist.append(tmpword)
        tmp_dict = {"name":file[:-4]}
        if DBG_OCR:
            print(nlist)
            print(rlist)
        for i in range(len(nlist)):
            # tmp_dict[nlist[i]] = round(float(rlist[i])/100.,4)  # 保留四位小数
            # tmp_dict[nlist[i]] = int(rlist[i])  # 字符串转换为整数
            tmp_dict[nlist[i]] = round(float(rlist[i]), 2)
        print(tmp_dict)
        res_list.append(tmp_dict)
        # break

    wt_xls(res_list,output_dir + '/sheet.xls')  # 存取识别结果到表格

    # 此处完成了OCR识别，接下来完成后续的可视化