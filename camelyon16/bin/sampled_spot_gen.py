import os
import sys
import logging
import argparse

import numpy as np
# 在癌症区域中，随机获取坐标点，然后将其保存为txt文本中.原代码前三个为必须输入参数。现改为可选参数。
# 根据掩码.npy得到正常区域和不正常区域的采样点的点集，存于txt中
# 以便在代码中输入固定的文件夹的位置
# 输入为**tumor.npy所在的文件夹  预计运行时间2s
sys.path.append(os.path.join(os.path.abspath(__file__), "/../../"))

parser = argparse.ArgumentParser(description="Get center points of patches "
                                             "from mask")
parser.add_argument("mask_path", default=None, metavar="MASK_PATH", type=str,
                    help="Path to the mask npy file")
parser.add_argument("txt_path", default=None, metavar="TXT_PATH", type=str,
                    help="Path to the txt file")
parser.add_argument("patch_number", default=None, metavar="PATCH_NUMB", type=int,
                    help="The number of patches extracted from WSI")
parser.add_argument("--level", default=6, metavar="LEVEL", type=int,
                    help="Bool format, whether or not")

class patch_point_in_mask_gen(object):
    '''
    extract centre point from mask
    inputs: mask path, centre point number
    outputs: centre point
    '''

    def __init__(self, mask_path, number):
        self.mask_path = mask_path
        self.number = number

    def get_patch_point(self):
        mask_tissue = np.load(self.mask_path)
        X_idcs, Y_idcs = np.where(mask_tissue)

        centre_points = np.stack(np.vstack((X_idcs.T, Y_idcs.T)), axis=1)

        if centre_points.shape[0] > self.number:
            sampled_points = centre_points[np.random.randint(centre_points.shape[0],
                                                             size=self.number), :]
        else:
            sampled_points = centre_points
        return sampled_points

def run(args):
    sampled_points = patch_point_in_mask_gen(args.mask_path, args.patch_number).get_patch_point()
    sampled_points = (sampled_points * 2 ** args.level).astype(np.int32) # make sure the factor

    mask_name = os.path.split(args.mask_path)[-1].split(".")[0]
    name = np.full((sampled_points.shape[0], 1), mask_name)
    center_points = np.hstack((name, sampled_points))

    txt_path = args.txt_path

    with open(txt_path, "a") as f:
        np.savetxt(f, center_points, fmt="%s", delimiter=",")

def main():
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    #----------------------------------------------------------------------------------------------
    mask_paths = 'path of mask-tumor'
    txt_paths = 'path of txt'
    for root,dirname,filenames in os.walk(mask_paths):
        for filename in filenames:
            args.mask_path = os.path.join(root,filename)
            args.txt_path = txt_paths +'/'+ filename.split('.')[0] +'_train_spot.txt'
            args.patch_number = 1000

    #----------------------------------------------------------------------------------------------
            run(args)

if __name__ == "__main__":
    main()
