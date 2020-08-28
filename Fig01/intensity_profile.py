# @SNTService snt

from ij import IJ
from sc.fiji.snt.analysis import PathProfiler
from sc.fiji.snt.util import PointInImage


# Retrieve image. NB: image has no spatial calibration by default and Z<>C
# channels are swapped. See http://cellimagelibrary.org/images/810
imp = IJ.openImage('https://cildata.crbs.ucsd.edu/media/images/810/810.tif')
imp.setDimensions(imp.getNSlices(), 1, 1)

# Trace segment
snt.initialize(imp, False)  # whether ui should be displayed 
path = snt.getPlugin().autoTrace(PointInImage(837,503,0), PointInImage(938,622,0), None)

# Profile tracing result
PathProfiler(path, imp).getPlot().show()
