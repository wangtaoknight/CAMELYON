import glob
import os
import sys
import logging
import argparse
import openslide
import numpy as np
import pandas as pd
import cv2
#-----------------------------------------------------------------------------------------------------------------------
# 功能：对输入的wsi(.tif利用生成概率图，也即热力图，提取features)
#   参考输入格式：(main()中自定义修改)
#         wsi_paths = '/home/public2/Lan/deepslide/input/test/'    # 测试WSI所在的路径
#         prob_map_paths = '/home/public2/Lan/data_camelyon16/probs_map/test/'    #对应概率图的保存文件夹 .npy文件
#         feature_paths = '/home/public2/Lan/data_camelyon16/feature_csv/test_feature/' #保存提取到的特征
#   此代码执行完后要将所有的特征文件(一个wsi对应一个.csv文件)，合并在一起，组成特征集，保存为一个.csv文件！！！！！！！！！！！！！！！！！！！
#   合并的特征的函数： ./data/move_json.py 中的bian_li()函数
#-----------------------------------------------------------------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')

# from camelyon16.data.wsi_producer import WSIPatchDataset  # noqa
from camelyon16.data.probs_ops import extractor_features


parser = argparse.ArgumentParser(description='Extract features from probability map'
                                             'for slide classification')
parser.add_argument('--probs_map_path', default=None, metavar='PROBS MAP PATH',
                    type=str, help='Path to the npy probability map ')
parser.add_argument('--wsi_path', default=None, metavar='WSI PATH',
                    type=str, help='Path to the whole slide image. ')
parser.add_argument('--feature_path', default=None, metavar='FEATURE PATH',
                    type=str, help='Path to the output features file')

probs_map_feature_names = ['region_count', 'ratio_tumor_tissue', 'largest_tumor_area', 'longest_axis_largest_tumor',
                           'pixels_gt_90', 'avg_prediction', 'max_area', 'mean_area', 'area_variance', 'area_skew',
                           'area_kurt', 'max_perimeter', 'mean_perimeter', 'perimeter_variance', 'perimeter_skew',
                           'perimeter_kurt', 'max_eccentricity', 'mean_eccentricity', 'eccentricity_variance',
                           'eccentricity_skew', 'eccentricity_kurt', 'max_extent', 'mean_extent', 'extent_variance',
                           'extent_skew', 'extent_kurt', 'max_solidity', 'mean_solidity', 'solidity_variance',
                           'solidity_skew', 'solidity_kurt', 'label']

def compute_features(extractor):
    features = []  # 总的特征

    probs_map_threshold_p90 = extractor.probs_map_set_p(0.9)
    probs_map_threshold_p50 = extractor.probs_map_set_p(0.5)

    region_props_p90 = extractor.get_region_props(probs_map_threshold_p90)
    region_props_p50 = extractor.get_region_props(probs_map_threshold_p50)

    f_count_tumor_region = extractor.get_num_probs_region(region_props_p90)  # 1
    features.append(f_count_tumor_region)

    f_percentage_tumor_over_tissue_region = extractor.get_tumor_region_to_tissue_ratio(region_props_p90)  # 2
    features.append(f_percentage_tumor_over_tissue_region)

    largest_tumor_region_index_t50 = extractor.get_largest_tumor_index(region_props_p50)
    f_area_largest_tumor_region_t50 = region_props_p50[largest_tumor_region_index_t50].area  # 3
    features.append(f_area_largest_tumor_region_t50)

    f_longest_axis_largest_tumor_region_t50 = extractor.get_longest_axis_in_largest_tumor_region(region_props_p50,
                                                                                                 largest_tumor_region_index_t50)  # 4
    features.append(f_longest_axis_largest_tumor_region_t50)

    f_pixels_count_prob_gt_90 = cv2.countNonZero(probs_map_threshold_p90)  # 5
    features.append(f_pixels_count_prob_gt_90)

    f_avg_prediction_across_tumor_regions = extractor.get_average_prediction_across_tumor_regions(region_props_p90)  # 6
    features.append(f_avg_prediction_across_tumor_regions)

    f_area = extractor.get_feature(region_props_p90, f_count_tumor_region, 'area')  # 7,8,9,10,11
    features += f_area

    f_perimeter = extractor.get_feature(region_props_p90, f_count_tumor_region, 'perimeter')  # 12,13,14,15,16
    features += f_perimeter

    f_eccentricity = extractor.get_feature(region_props_p90, f_count_tumor_region, 'eccentricity')  # 17,18,19,20,21
    features += f_eccentricity

    f_extent_t50 = extractor.get_feature(region_props_p50, len(region_props_p50), 'extent')  # 22,23,24,25,26
    features += f_extent_t50

    f_solidity = extractor.get_feature(region_props_p90, f_count_tumor_region, 'solidity')  # 27,28,29,30,31
    features += f_solidity

    return features

def run(args):
    slide_path = args.wsi_path

    probs_map = np.load(args.probs_map_path)

    extractor = extractor_features(probs_map, slide_path)

    features = compute_features(extractor)

    wsi_name = os.path.split(args.wsi_path)[-1]
    if 'umor' in wsi_name:
        features += [1]
    elif 'ormal' in wsi_name:
        features += [0]
    else:
        features += ['Nan']

    df = (pd.DataFrame(data=features)).T
    df.to_csv(args.feature_path, index=False, sep=',')

def main():
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    #-------------------------------------------------------------------------------------------------------------------
    wsi_paths = '/home/public2/Lan/deepslide/input/test/'
    prob_map_paths = '/home/public2/Lan/data_camelyon16/probs_map/test/'
    feature_paths = '/home/public2/Lan/data_camelyon16/feature_csv/test_feature/'

    paths = glob.glob(prob_map_paths+ '*.npy')
    for path in paths:
        args.probs_map_path = path
        name = path.split('/')[-1]
        args.wsi_path = wsi_paths + 'test_'+ name.split('_')[1]+ '.tif'
        args.feature_path = feature_paths +'test_'+ name.split('_')[1]+ '.csv'

    #-------------------------------------------------------------------------------------------------------------------
        run(args)


if __name__ == '__main__':
    main()
