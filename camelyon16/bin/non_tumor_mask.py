import sys
import os
import argparse
import logging

import numpy as np
# 程序主要是获取wsi中除去癌组织(ROI)和背景之后的正常组织(nomal)掩码。以便下一步从这些正常区域中生成，产生normal—patch所需要的点
# 同理，本代码中，将必须输入参数改为可选参数，然后在程序中定义输入参数的值。以便程序执行。
# 输入路径tumor和tissue两个之前生成了的掩码，提取tumor组织中正常的组织掩码
# 服务器运行代码 2s左右
#      输入示范:
#         all_tissue_paths = 'path of tissue'
#         all_tumor_paths = 'path of tumors'
#         jiehe_paths = 'path of jiehe'   #用以保存normal掩码的文件位置。此处命名不清晰。

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
parser = argparse.ArgumentParser(description="Get the normal region"
                                             " from tumor WSI ")
parser.add_argument("--tumor_path", default=None, metavar='TUMOR_PATH', type=str,
                    help="Path to the tumor mask npy")
parser.add_argument("--tissue_path", default=None, metavar='TISSUE_PATH', type=str,
                    help="Path to the tissue mask npy")
parser.add_argument("--normal_path", default=None, metavar='NORMAL_PATCH', type=str,
                    help="Path to the output normal region from tumor WSI npy")
def run(args):
    tumor_mask = np.load(args.tumor_path)
    tissue_mask = np.load(args.tissue_path)
    normal_mask = tissue_mask & (~ tumor_mask)
    np.save(args.normal_path, normal_mask)

def main():
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    #------------------------------------------------------------------------------------------------------------------\
    all_tissue_paths = 'path of tissue'
    all_tumor_paths = 'path of tumors'
    jiehe_paths = 'path of jiehe'

    for root,dirname,filenames in os.walk(all_tissue_paths):
        for filename in filenames:
            args.wsi_path = os.path.join(root,filename)
            args.json_path = all_tumor_paths +'/'+filename.split('_')[0]+'_'+filename.split('_')[1] +'_tumor.npy'
            args.npy_path = jiehe_paths +'/'+ filename.split('_')[0]+'_'+filename.split('_')[1] +'_normal.npy'
    #------------------------------------------------------------------------------------------------------------------\
    run(args)

if __name__ == "__main__":
    main()
