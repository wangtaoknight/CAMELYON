import sys
import os
import argparse
import logging

'''
    说明：本程序的主要用于将camelyon16中的xml注释转为json注释。
    程序接口：直接给出xml所在和json要保存文件的文件夹路径(文件夹)
    原程序默认命令：python CAMELYON16/camelyon16/bin/camelyon16xml2json.py Tumor_001.xml Tumor_001.json
    是读取单张xml文件将其保存在特定文件夹中(.json)。本次改为在程序中提供文件夹即可。
    输入文件夹参考格式：
        xml_paths = 'F:/camelyon_tumor/zhus/'    #xml的文件夹
        josn_paths = 'F:/camelyon_tumor/json/'   #保存到目标文件夹
    因为程序主要在Ubuntu上运行，如果在windows上运行，可能因'\\'，发生路径出错          2020.08.27
'''

# 作用是将另一个文件夹(data)中的.py中的函数引入
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../../')

from camelyon16.data.annotation import Formatter  # noqa

# parser = argparse.ArgumentParser(description='Convert Camelyon16 xml format to'
#                                  'internal json format')
# parser.add_argument('xml_path', default=None, metavar='XML_PATH', type=str,
#                     help='Path to the input Camelyon16 xml annotation')
# parser.add_argument('json_path', default=None, metavar='JSON_PATH', type=str,
#                     help='Path to the output annotation in json format')


def run(args):
    Formatter.camelyon16xml2json(args.xml_path, args.json_path)


def main():
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    #-------------------------------------------------------------------------------------------------------------------
    # run(args)
    # 定义xml、json文件的输入文件夹  运行代码时将以下两个路径改为自己的路径即可。
    # xml_paths是xml文件的所在的文件夹路径 josn_paths是json文件想要保存的路径
    xml_paths = 'F:/camelyon_tumor/zhus/'
    josn_paths = 'F:/camelyon_tumor/json/'
    for root,dirname,filenames in os.walk(xml_paths):
        for filename in filenames:
            args.xml_path = os.path.join(root,filename)
            args.json_path = josn_paths +'/' + filename.split('.')[0]+'.json'
            run(args)
    #-------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
