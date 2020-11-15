import pytesseract
from PIL import Image
import numpy as np
import cv2
import img_preprocess as ip

pytesseract.pytesseract.tesseract_cmd = 'D:/TesseractOCR/Tesseract-OCR/tesseract.exe'
tessdata_dir_config = '--tessdata-dir "D:/TesseractOCR/Tesseract-OCR/tessdata"'

raw_image = Image.open("./pictures/2010_Q1.jpg")
image = np.array(raw_image)
for m in range(image.shape[0]):
    for n in range(image.shape[1]):
        tmp_px = image[m,n,:]
        if ((tmp_px[0] < 60) and (tmp_px[1] < 60) and (tmp_px[2] < 60)):
            pass
        else:
            image[m, n, :] = [255,255,255]

img = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
# cv2.imshow("color_filter",img)
cv2.imwrite("./tmp_result/color_filter.jpg",img)
blurred = cv2.GaussianBlur(img, (3, 3), 0)
gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
# cv2.imshow("gray",gray)
cv2.imwrite("./tmp_result/gray.jpg",gray)

# output_gray = ip.laplace_sharpen(gray,1) # 拉普拉斯锐化
# cv2.imshow("output_gray",output_gray)
binary_img = ip.adaptive_threshold(gray, blockSize=15) # 二值化
# ip.get_projection_list_demo(binary_img) # 画出投影
# cv2.imshow("binary",binary_img)
# cv2.waitKey()
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
erode_img = cv2.erode(binary_img, kernel)
# ip.get_projection_list_demo(erode_img) # 画出投影
# cv2.imshow("erode_img",erode_img)


H = 'horizontal'
V = 'vertical'
root = ip.cut_binary_img1(erode_img, 0, 0, direction=H, iteration=2)
rects = ip.get_leaf_node(root)
new_img = ip.draw_rects(img, rects)
# get_projection_list_demo(binary_img)

# cv2.imshow('new_img', new_img)
cv2.imwrite("./tmp_result/new_img.jpg",new_img)
# cv2.imshow('src', img)
# cv2.imshow('erode_img', erode_img)
# cv2.imshow('binary_img', binary_img)
cv2.imwrite("./tmp_result/binary_img.jpg",binary_img)
# cv2.waitKey(0)