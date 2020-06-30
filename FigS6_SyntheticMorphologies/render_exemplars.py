from sc.fiji.snt import Tree
from sc.fiji.snt.analysis import TreeAnalyzer
from sc.fiji.snt.viewer import (MultiViewer2D, Viewer2D)
import os

in_dir = r"/home/tferr/code/morphonets/SNTmanuscript/FigS6_SyntheticMorphologies/swc/"
out_dir = r"/home/tferr/code/morphonets/SNTmanuscript/FigS6_SyntheticMorphologies/"

all_grns = []
for swc_file in os.listdir(in_dir):
	if swc_file.endswith(".swc"):
		t = Tree(in_dir + '/' + swc_file)
		all_grns.append(t)

grn0 = [t for t in all_grns if 'grn_0' in t.getLabel()]
grn1 = [t for t in all_grns if 'grn_1' in t.getLabel()]
grn2 = [t for t in all_grns if 'grn_2' in t.getLabel()]
grn3 = [t for t in all_grns if 'grn_3' in t.getLabel()]
grn4 = [t for t in all_grns if 'grn_4' in t.getLabel()]

grns =      [grn0,  grn1,  grn2,  grn3,  grn4]
xoffsets =  [10,    100,   0,     40,    0]
yspacings = [0,     0,     80,    0,     80] 
scales =    [1,     1,     2.2,   1,     2.2]
labels =    ["GRN2","GRN3","GRN5","GRN1","GRN4"] #labels assigned in legend (density-sorted)


for grn_idx, grn in enumerate(grns):
    align_to = grn[0].getRoot()
    for i in range(1, len(grn)):
        cur_root = grn[i].getRoot()
        grn[i].translate(align_to.getX()-cur_root.getX(), align_to.getY()-cur_root.getY(), align_to.getZ()-cur_root.getZ())

    colors = ["red", "blue", "black"]
    grn = sorted(grn, key=lambda x: -TreeAnalyzer(x).getCableLength())
    v = Viewer2D()
    for tree_idx, tree in enumerate(grn):
        grn[tree_idx].translate(xoffsets[grn_idx], yspacings[grn_idx]*tree_idx, 0)
        grn[tree_idx].scale(scales[grn_idx], scales[grn_idx], scales[grn_idx])
        v.add(grn[tree_idx], colors[tree_idx])

    ## Customize rendering
    chart = v.getChart()
    chart.setAxesVisible(False)
    chart.setGridlinesVisible(False)
    chart.setOutlineVisible(False)
    width = 530 *2
    height = 900*2 if yspacings[grn_idx] > 0 else 700*2
    chart.show(width, height)
    chart.saveChartAsPNG(out_dir + "/" + labels[grn_idx])

