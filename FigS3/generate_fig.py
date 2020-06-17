# @Context context
# @LegacyService ls
# @SNTService snt

import os
import inspect

import ij
from ij.gui import Overlay
from sc.fiji.snt.analysis import TreeColorMapper, PathProfiler, RoiConverter

fig_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda: 0)))
traces_dir = fig_dir + '/traces'

mitosis_img_url = "http://wsr.imagej.net/images/mitosis.tif"
img = ij.IJ.openImage(mitosis_img_url)
snt.initialize(img, True)  # Image stack, whether ui should be displayed.

for f in os.listdir(traces_dir):
    traces_file = traces_dir + '/' + f
    snt.loadTracings(traces_file)

tree = snt.getTree(False)  # selected paths only?

img.setPosition(tree.get(0).getChannel(), 3, tree.get(0).getFrame())

mapper = TreeColorMapper(context)
mapper.map(tree, TreeColorMapper.LENGTH, 'Thermal.lut')

profiler = PathProfiler(tree, img)
profiler.assignValues()

snt.getStatistics(False).getHistogram("Node intensity values").show()

img.setOverlay(Overlay())
converter = RoiConverter(tree, img)
converter.convertPaths(img.getOverlay())