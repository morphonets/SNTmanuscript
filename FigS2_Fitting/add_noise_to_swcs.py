# @File(label="Directory containing the Gold Standard SWCs", style="directory") swc_dir

import os
import shutil
import random
import re

from sc.fiji.snt import Tree
from sc.fiji.snt.util import PointInImage

max_dist = 0.5  # maximum allowed shift along any axis


def add_noise_to_tree(tree):

    for path in tree.list():
        for i in range(path.size()):
            node = path.getNode(i)
            new_x = node.x + random.uniform(-1 * max_dist, max_dist)
            new_y = node.y + random.uniform(-1 * max_dist, max_dist)
            new_z = node.z + random.uniform(-1 * max_dist, max_dist)
            path.moveNode(i, PointInImage(new_x, new_y, new_z))
            
    return tree


def get_swc_files(dir):

    swc_list = []
    for f in os.listdir(dir):
        filepath = dir + '/' + f
        if os.path.isfile(filepath) and filepath.endswith(".swc"):
            swc_list.append(filepath)

    return swc_list


def run():

    swcs = get_swc_files(str(swc_dir))
    output_dir = str(swc_dir) + '/noisy_gs' 
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    for swc in swcs:
        tree = Tree(swc)
        tree.scale(0.3296485, 0.3296485, 0.998834955)
        cell_number = re.search("OP_(\d)", tree.getLabel()).group(1)
        noisy_tree = add_noise_to_tree(tree)
        output_filepath = output_dir + '/OP_{}_noisy.swc'.format(cell_number)
        success = "File saved" if noisy_tree.saveAsSWC(output_filepath) else "unsaved result. I/O error?"
        print(success)

    
run()
