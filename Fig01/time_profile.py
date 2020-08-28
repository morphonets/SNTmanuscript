# @SNTService snt

import os
import inspect
from ij import IJ
from sc.fiji.snt import PathManagerUI


# Retrieve traces file
fig_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda: 0)))
traces_file = os.path.join(fig_dir, "traces", "701.traces")

# Retrieve image. NB: image has no spatial/temporal calibration by default
# see http://cellimagelibrary.org/images/701
try:
    imp = IJ.openImage('https://cildata.crbs.ucsd.edu/media/images/701/701.tif')
    dims = imp.getDimensions()
    imp.setDimensions(1, 1, imp.getNSlices())
    snt.initialize(imp, True)  # whether ui should be displayed
except:
    snt.initialize(True)  # image could not be retrieve. Use canvas instead
finally:
    snt.loadTracings(traces_file)

# Apply Path Manager's Tag>Image Metadata> command
pm_ui = snt.getUI().getPathManager()
pm_ui.selectAll()
pm_ui.runCommand("Traced Frame")

# Run Path Manager's Analyze>Color Coding... command
pm_ui.runCommand("Color Code Path(s)...", "Path frame", "mpl-viridis.lut")

# Options: Metric: Cable Length; Grouping Strategy: "Matched path(s) across time";
pm_ui.runCommand("Time Profile...",)
