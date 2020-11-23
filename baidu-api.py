# coding=utf-8

import sys
import os
import json
import base64
import time
import xlwt
import copy

# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# 防止https证书校验不正确
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = 'qfG12QHB37jGVqlvGxISuU1W'

SECRET_KEY = 'EDypY2a7EGlIK7NYIw8GltgZadihuan8'

OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"

"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

"""
    获取token
"""


def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()

    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print('please overwrite the correct API_KEY and SECRET_KEY')
        exit()


"""
    读取文件
"""


def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


"""
    调用远程服务
"""


def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)


def wt_xls(AllData):
    workbook = xlwt.Workbook(encoding='ascii')
    worksheet = workbook.add_sheet('My Worksheet')
    print(AllData)

    tag = []  # 浏览器种类
    for i in range(len(AllData)):
        for dict_key in AllData[i].keys():
            if tag.count(dict_key) == 0:
                tag.append(dict_key)
    # print(tag)

    for i in range(len(tag)):
        worksheet.write(i, 0, tag[i])

    ans = []  # 最终使用的字典列表，更新后写入xls
    tmp = dict.fromkeys(tag, 0.0)
    for i in range(len(AllData)):
        ans.append(copy.deepcopy(tmp))
    # print(ans)

    for i in range(len(AllData)):
        for key in AllData[i].keys():
            # print(key, AllData[i][key])
            ans[i][key] = AllData[i][key]

    for i in range(len(ans)):
        for j in range(len(tag)):
            worksheet.write(j, i + 1, ans[i][tag[j]])

    workbook.save('result1.xls')  # 保存文件


if __name__ == '__main__':

    # 获取access token
    token = fetch_token()

    # 拼接通用文字识别高精度url
    image_url = OCR_URL + "?access_token=" + token
    # 停用词
    stopwords = [" Popular", " Internet", " Browsers", "e"]
    res_list = []
    path = "./result/pictures/"
    dirs = os.listdir(path)
    for file in dirs:
        print(file[:-4])
        file_content = read_file(path + file)
        text = ""
        # 调用文字识别服务
        result = request(image_url, urlencode({'image': base64.b64encode(file_content)}))
        nlist = []
        rlist = []

        # 解析返回结果
        result_json = json.loads(result)
        for words_result in result_json["words_result"]:
            if words_result["words"] not in stopwords:
                if words_result["words"].find('.') >= 0:
                    if len(text):
                        if text.find("Navigator") >= 0:
                            text = "Netscape Navigator"
                        nlist.append(text.strip(' '))
                        text = ""
                    rlist.append(words_result["words"])
                else:
                    text = text + " " + words_result["words"]
        rlist = rlist[6:]
        tmp_dict = {"name": file[:-4]}
        for i in range(len(nlist)):
            tmp_dict[nlist[i]] = round(float(rlist[i].strip('%')) / 100.,4)
        res_list.append(tmp_dict)
        print(tmp_dict)
        time.sleep(2)

    # print(res_list)
    wt_xls(res_list)
