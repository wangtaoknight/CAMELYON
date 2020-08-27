import os
import sys
import logging
import argparse

import numpy as np
import openslide
import cv2
import json

#-----------------------------------------------------------------------------------------------------------
'''利用json注释、tif病理图像，获取癌症掩码npy。以便进一步在在癌症区域中生成产生patch所需要用以定位的点
这里将单幅转换改为文件下遍历转换。在main()函数中输入
输入示范:
    wsi_path = 'F:/camelyon_tumor/train/tumor'
    json_path = 'F:/camelyon_tumor/json'
    mask_npys = 'F:/camelyon_tumor/mask_npy'
'''
#-----------------------------------------------------------------------------------------------------------

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')

parser = argparse.ArgumentParser(description='Get tumor mask of tumor-WSI and '
                                             'save it in npy format')
parser.add_argument('--wsi_path', default=None, metavar='WSI_PATH', type=str,
                    help='Path to the WSI file')
parser.add_argument('--json_path', default=None, metavar='JSON_PATH', type=str,
                    help='Path to the JSON file')
parser.add_argument('--npy_path', default=None, metavar='NPY_PATH', type=str,
                    help='Path to the output npy mask file')
parser.add_argument('--level', default=6, type=int, help='at which WSI level'
                    ' to obtain the mask, default 6')


def run(args):

    # get the level * dimensions e.g. tumor0.tif level 6 shape (1589, 7514)
    slide = openslide.OpenSlide(args.wsi_path)
    w, h = slide.level_dimensions[args.level]
    mask_tumor = np.zeros((h, w)) # the init mask, and all the value is 0

    # get the factor of level * e.g. level 6 is 2^6
    factor = slide.level_downsamples[args.level]


    with open(args.json_path) as f:
        dicts = json.load(f)
    tumor_polygons = dicts['positive']

    for tumor_polygon in tumor_polygons:
        # plot a polygon
        name = tumor_polygon["name"]
        vertices = np.array(tumor_polygon["vertices"]) / factor
        vertices = vertices.astype(np.int32)

        cv2.fillPoly(mask_tumor, [vertices], (255))

    mask_tumor = mask_tumor[:] > 127
    mask_tumor = np.transpose(mask_tumor)

    np.save(args.npy_path, mask_tumor)

def main():
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    #-------------------------------------------------------------------------------------------------------------------
    wsi_path = 'F:/camelyon_tumor/train/tumor'
    json_path = 'F:/camelyon_tumor/json'
    mask_npys = 'F:/camelyon_tumor/mask_npy'
    for root,dirname,filenames in os.walk(wsi_path):
        for filename in filenames:
            args.wsi_path = os.path.join(root,filename)
            args.json_path = json_path +'/'+filename.split('.')[0]+'.json'
            args.npy_path = mask_npys +'/'+ filename.split('.')[0]+'_tumor.npy'
    #-------------------------------------------------------------------------------------------------------------------
            run(args)

if __name__ == "__main__":
    main()
