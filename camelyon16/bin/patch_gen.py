import sys
import os
import time
import argparse
import logging
import time
from shutil import copyfile
from multiprocessing import Pool, Value, Lock

import openslide
#-------------------------------------------------------------------------------------------------------Authour：WT
# 预计代码运行时间 905s
# 此程序的作用是利用前面生成的组织中的采样点坐标，在对应的WSI文件中采样patch，并保存为jpg图像
# 修改代码时，主要修改两个地方：
#    1 修改文件接口，将wsi文件改为对应路径，对应txt文件的路径，patch保存路径
#    2 修改process中的代码，修改生成wsi_path的代码，根据自己的需要看是否修改。读取文件直接有路径拼接，.pilt()[i]，这个i不对导致错误
#         (此处易出现bug，因为路径变化，程序逻辑也会变，此处还未修改好-便于移植。仅自己使用时修改好了，如有问题在process中根据提示修改即可)
#--------------------------------------------------------------------------------------------------------Authour：WT
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
parser = argparse.ArgumentParser(description='Generate patches from a given '
                                 'list of coordinates')
parser.add_argument('wsi_path', default=None, metavar='WSI_PATH', type=str,
                    help='Path to the input directory of WSI files')
parser.add_argument('coords_path', default=None, metavar='COORDS_PATH',
                    type=str, help='Path to the input list of coordinates')
parser.add_argument('patch_path', default=None, metavar='PATCH_PATH', type=str,
                    help='Path to the output directory of patch images')
parser.add_argument('--patch_size', default=256, type=int, help='patch size, '
                    'default 768')
parser.add_argument('--level', default=0, type=int, help='level for WSI, to '
                    'generate patches, default 0')
parser.add_argument('--num_process', default=5, type=int,
                    help='number of mutli-process, default 5')
count = Value('i', 0)
lock = Lock()

def process(opts):
    i, pid, x_center, y_center, args = opts
    x = int(int(x_center) - args.patch_size / 2)
    y = int(int(y_center) - args.patch_size / 2)
    wsi_path = os.path.join(args.wsi_path,'tumor_'+ pid.splid('_')[0] + '.tif')
    slide = openslide.OpenSlide(wsi_path)
    img = slide.read_region(
        (x, y), args.level,
        (args.patch_size, args.patch_size)).convert('RGB')
    img.save(os.path.join(args.patch_path, str(i) + '.png'))
    global lock
    global count
    with lock:
        count.value += 1
        if (count.value) % 100 == 0:
            logging.info('{}, {} patches generated...'
                         .format(time.strftime("%Y-%m-%d %H:%M:%S"),
                                 count.value))

def run(args):
    logging.basicConfig(level=logging.INFO)
    # 下一行代码的作用是，如果保存patch的目标文件夹不存在，则创建这个文件夹
    if not os.path.exists(args.patch_path):
        os.mkdir(args.patch_path)
    copyfile(args.coords_path, os.path.join(args.patch_path, 'list.txt'))
    opts_list = []
    infile = open(args.coords_path)
    for i, line in enumerate(infile):
        pid, x_center, y_center = line.strip('\n').split(',')
        opts_list.append((i, pid, x_center, y_center, args))
    infile.close()
    pool = Pool(processes=args.num_process)
    pool.map(process, opts_list)

def main():
    args = parser.parse_args()
    #-------------------------------------------------------------------------------------------------------------------
    args.wsi_path = 'path to all WSI'     # wsi文件所在的位置
    arg.patch_path = 'path of dir to save patch'          # 生成patch要保存的文件夹的位置
    txt_path = 'path of txt'                              # 所需位置点集文件

    for root,dirname,filenames in os.walk(txt_path):
        for filename in filenames:
            args.coords_path = os.path.join(root, filename)
    #-------------------------------------------------------------------------------------------------------------------
            run(args)

if __name__ == '__main__':
    start = time.time()
    main()
    print('All time_gen_patch:%ds'%(time.time()-start))