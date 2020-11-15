import matplotlib.pyplot as plt
import xlrd
import copy
from matplotlib import cm
import numpy as np
from matplotlib import font_manager as fm


'''
    各种文件路径
'''
wb = xlrd.open_workbook(r'.\result\sheet.xls')  # 打开Excel文件
sheet = wb.sheet_by_name(r'My Worksheet')  # 通过excel表格名称(rank)获取工作表

plt_path = '.\\result\\pic\\plt_x.png'  # 写路径
pie_path = '.\\result\\pic\\pie_x.jpg'
text_path = '.\\result\\text.txt'

row = []  # 创建list存放源数据
col = []
'''
    统计量
'''
vanished = []       # 消失的名字
best = ""           # 暂存最高值的key
highest = 0         # 暂存最高值的value
history_name = []   # 值最高的名字
history_time = []   # 名字对应的时间

'''
  读表格，存放到列表中，row 里面的东西是横的。col 里是竖的
'''
for a in range(sheet.nrows):  # 循环读取表格内容（每次读取一行数据）
    cells = sheet.row_values(a)  # 每行数据赋值给cells
    if sheet.cell_value(a, 0) != 'name':
        row.append(cells[2:])  # 把每次循环读取的数据插入到row
for a in range(sheet.ncols):
    cells = sheet.col_values(a)
    col.append(cells)

for i in range(len(col[-1])):
    if col[-1][i] == 0:
        vanished.append(col[0][i])
# print(vanished)

global_labels = copy.deepcopy(col[0])
global_labels.remove('name')
# print(global_labels)


colors = cm.rainbow((np.arange(len(row))) / len(row))  # set colors

MaxSize = len(col)
print(MaxSize)

plt.style.use('seaborn')

for j in range(1, MaxSize + 1):                  # 绘制小折线图
    plt.figure(figsize=(5, 4))
    for i in range(len(row)):
        plt.plot(row[i][0:j], '-', color=colors[i])
    plt.legend(global_labels, loc="best", fontsize='x-small')
    plt.savefig(plt_path.replace('x', str(j-1)))
    # plt.show()
    plt.close()

plt.figure(figsize=(20, 12))
for i in range(len(row)):                       # 绘制总折线图
    plt.plot(row[i], '-o', color=colors[i])
    plt.legend(global_labels, loc="best", fontsize='x-large')
    plt.savefig(plt_path)
    plt.title("最受欢迎的浏览器", loc='center', fontsize=30)
    plt.rcParams['font.sans-serif'] = ['SimHei']    # 显示中文标签
    plt.rcParams['axes.unicode_minus'] = False      # 这两行需要手动设置

# print(row)
# print(col)


for i in range(MaxSize - 1):                    # 绘制所有饼状图
    tmp_dict = dict(zip(col[0], col[i + 1]))
    for key in list(tmp_dict.keys()):
        if not tmp_dict.get(key):
            del tmp_dict[key]
    title = tmp_dict['name']
    del tmp_dict['name']

    for key, value in tmp_dict.items():         # 统计数据
        if value == max(tmp_dict.values()):
            max_key = key
            if max_key != best:
                best = max_key
                history_name.append(max_key)
                history_time.append(title)
    # print(tmp_dict)
    zeroArray = [0.0 for i in range(len(tmp_dict))]
    explode = np.arange(len(zeroArray)) / len(zeroArray) / len(zeroArray) / 3
    # print(explode)
    # print(zeroArray)

    for j in range(len(zeroArray)):                     # 设置饼状图裂开程度
        zeroArray[j] = explode[j]
    colors = cm.rainbow(np.arange(len(tmp_dict)) / len(tmp_dict))
    nums = list(tmp_dict.values())
    labels = list(tmp_dict.keys())
    plt.figure(figsize=(20, 12))                        # 2000 * 1200
    patches, texts, autotexts = plt.pie(nums, labels=labels, autopct='%3.2f%%', colors=colors, explode=zeroArray)
    plt.axis('equal')

    plt.title(title, loc='center', fontsize=30)
    proptease = fm.FontProperties()
    proptease.set_size('xx-large')
    # font size include: ‘xx-small’,x-small’,'small’,'medium’,‘large’,‘x-large’,‘xx-large’ or number, e.g. '12'
    plt.setp(autotexts, fontproperties=proptease)
    plt.setp(texts, fontproperties=proptease)
    plt.legend(labels, loc=1, fontsize=15)
    # plt.tight_layout()
    plt.savefig(pie_path.replace('x', str(i)))
    # plt.show()
    plt.close()


text = "\n\t\n\t\nWe Found That:\n\n"
print(history_time)
print(history_name)
history_time.append("Now")
for i in range(len(history_name)):
    text = text + "From " + history_time[i] + " To " + history_time[i+1] + ",\n\t" + history_name[i] + " is the most popular browser.\n"

print(vanished)
text = text + "\n\nThe ones that disappeared in history:\n"
for i in range(len(vanished)):
    text = text + '\t' + vanished[i]
    if i % 2 == 0:
        text = text + '\n'
text = text + "\n\n   Group Members: csq zzp hzh hyk\n   Thanks For Watching!!!"
print(text)
f = open(text_path, 'r+', encoding='utf-8')
f.write(text)
f.close()
