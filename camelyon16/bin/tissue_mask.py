import sys
import os
import argparse
import logging

import numpy as np
import openslide
from skimage.color import rgb2hsv
from skimage.filters import threshold_otsu
'''
    获得.tif文件在特定level(默认6)下的组织掩码 .npy
'''


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')

parser = argparse.ArgumentParser(description='Get tissue mask of WSI and save'
                                 ' it in npy format')
parser.add_argument('wsi_path', default=None, metavar='WSI_PATH', type=str,
                    help='Path to the WSI file')
parser.add_argument('npy_path', default=None, metavar='NPY_PATH', type=str,
                    help='Path to the output npy mask file')
parser.add_argument('--level', default=6, type=int, help='at which WSI level'
                    ' to obtain the mask, default 6')
parser.add_argument('--RGB_min', default=50, type=int, help='min value for RGB'
                    ' channel, default 50')
#--------------------------------------------------------------------------------
# 以下代码为在尽量不改动源代码的情况下，将其改为自己需要的代码。上面的代码主要为文件路径输入函数，需要
# 在文件路径中进行指定。因为使用命令行参数不方便，这里在不改变源代码的情况下(主要考虑后面继续修改)，
# 进行修改，使得其可以满足需求-在代码中定义文件输入路径。同时，因为源代码为单幅路径进行转换，这
# 里整个文件夹下.tif自动全部进行转换。wsi_path npy_path为必选参数，这里加--变为可选参数
#           服务器处理时间预计：390s
#--------------------------------------------------------------------------------


def run(args):
    logging.basicConfig(level=logging.INFO)

    slide = openslide.OpenSlide(args.wsi_path)

    # note the shape of img_RGB is the transpose of slide.level_dimensions
    img_RGB = np.transpose(np.array(slide.read_region((0, 0),
                           args.level,
                           slide.level_dimensions[args.level]).convert('RGB')),
                           axes=[1, 0, 2])

    img_HSV = rgb2hsv(img_RGB)

    background_R = img_RGB[:, :, 0] > threshold_otsu(img_RGB[:, :, 0])
    background_G = img_RGB[:, :, 1] > threshold_otsu(img_RGB[:, :, 1])
    background_B = img_RGB[:, :, 2] > threshold_otsu(img_RGB[:, :, 2])
    tissue_RGB = np.logical_not(background_R & background_G & background_B)
    tissue_S = img_HSV[:, :, 1] > threshold_otsu(img_HSV[:, :, 1])
    min_R = img_RGB[:, :, 0] > args.RGB_min
    min_G = img_RGB[:, :, 1] > args.RGB_min
    min_B = img_RGB[:, :, 2] > args.RGB_min

    tissue_mask = tissue_S & tissue_RGB & min_R & min_G & min_B

    np.save(args.npy_path, tissue_mask)


def main():
    args = parser.parse_args()
    #-------------------------------------------------------------------------------------------------------------------
    all_wsi_path = 'F:/camelyon_tumor/tumor'
    all_wsi_npy = 'F:/camelyon_tumor/all_npy'
    for root,dirname,filenames in os.walk(all_wsi_path):
        for filename in filenames:
            args.wsi_path = os.path.join(root,filename)
            args.npy_path = all_wsi_npy +'/'+filename.split('.')[0] + '_tissue.npy'
            args.level = 6
    #-------------------------------------------------------------------------------------------------------------------
            run(args)


if __name__ == '__main__':

    main()
