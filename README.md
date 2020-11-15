# dataIsBeautiful-ocr
- 提取data is beautiful视频中的数据并生成静态表格和演示视频

# How To Run
``` python
python main.py
```
## Parameters
- `-video`: data is beautiful视频存放路径，默认为`./videos/browsers.mp4`
- `-output_dir`: 结果输出路径，默认为`./result`
- `-save_tmp` :是否文字检测的中间过程，默认为`1`

## Requirements
- opencv_python==4.4.0.46
- numpy==1.19.4
- pytesseract==0.3.6
- scikit_image==0.17.2
- torchvision==0.8.1+cu101
- xlwt==1.3.0
- matplotlib==3.3.2
- torch==1.7.0+cu101
- python_bidi==0.4.2
- six==1.14.0
- pathlib2==2.3.5
- Pillow==8.0.1
- PyYAML==5.3.1
- skimage==0.0
