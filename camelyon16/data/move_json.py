import os
import shutil
import glob
import numpy as np
import matplotlib.pylab as plt
import pandas as pd

# 因为patch的数量太大，动辄上万张，在用UI界面进行剪切复制的时候很容易卡顿，所以写程序进行批处理
# 本程序可以运行移动指定类型文件到指定目录下
# 程序预计时间 1S

def move_jpg():
    sr_path = 'F:/camelyon_tumor/train/valid_patch/normal'
    aim_path = 'path of aim'
    i=1
    for folderName, subfolders, filenames in os.walk(sr_path):
        print(folderName)
        for filename in filenames:
            if i>14608:
                break
            if '.jpg' in filename:
                print(filename)
                try:
                    shutil.move(folderName+'/'+filename,aim_path +'/'+filename)
                    i +=1
                except OSError:
                    print('出错！')

def copy_file(sr_path,aim_path):
    # 此函数定义为将sr_path下的文件复制到aim_path文件夹下
    # 使用的时候定义源文件夹、目的文件夹即可
    i=1
    for folderName, subfolders, filenames in os.walk(sr_path):
        print(folderName)
        for filename in filenames:
            if i>14608:
                break
            if '.xml' in filename:
                print(filename)
                try:
                    shutil.copy2(folderName+'/'+filename,aim_path +'/'+filename)
                    i +=1
                except OSError:
                    print('出错！')

def bian_li():
    # 此程序将分离的.csv文件中的特征合在一起
    sr_path = 'G:/feature_csv/train_features/'  # 要和并的.csv特征集
    aim_path = 'G:/feature_csv/'                # 保存的文件夹
    filename = 'train_features.csv'           # 合并之后的文件名

    paths = glob.glob(sr_path+'\\*.csv')
    fir_file = pd.read_csv( paths[0])
    fir_file.to_csv(aim_path+ '/'+ filename,encoding="utf_8_sig",index=False)
    for i in range(1,len(paths)):
        fir_file = pd.read_csv(paths[i],index_col=False)
        fir_file.to_csv(aim_path+ '/'+ filename,encoding="utf_8_sig",index=False, mode='a+',header=None)

def show_heatmap(tu_path):
    heat = np.load(tu_path)
    col = 'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Vega10', 'Vega10_r', 'Vega20', 'Vega20_r', 'Vega20b', 'Vega20b_r', 'Vega20c', 'Vega20c_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spectral', 'spectral_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'viridis', 'viridis_r', 'winter', 'winter_r'
    col = list(col)
    for color in col:
        # plt.subplot(2,1,1)
        # xs = plt.matshow(heat)
        # xs.set_cmap(color)
        # plt.colorbar()
        # plt.subplot(2,1,2)
        plt.imshow(heat, cmap=plt.cm.jet) # 蓝红显示效果较好
        plt.colorbar()
        plt.show()
        break # 用以停止显示其他种类的颜色

if __name__ == '__main__':
    # tu_path = 'F:/camelyon_tumor/tumor/tumor_039_probs_map.npy'
    # sr_path = 'F:/camelyon_tumor/tumor/zhus/'
    # aim_path = 'F:/camelyon_tumor/json/ceshi/'
    # copy_file(sr_path=sr_path,aim_path=aim_path)
    # bian_li()
    sr_path = 'F:/camelyon_tumor/tumor/cs/tumor_097_probs_map.npy'
    show_heatmap(sr_path)