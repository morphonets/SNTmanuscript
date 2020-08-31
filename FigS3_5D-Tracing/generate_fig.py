# @Context context
# @SNTService snt

import inspect
import os
import time
import sc.fiji.snt.PathManagerUI


# Load files
mitosis_img_url = "http://wsr.imagej.net/images/mitosis.tif"

fig_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda: 0)))
traces_file = os.path.join(fig_dir, "traces", "mitosis.traces")

snt.initialize(mitosis_img_url, True)  # Path to image, whether ui should be displayed
time.sleep(3) # ensure GUI has been displayed
snt.loadTracings(str(traces_file))

# Set options and access the "Path Manager" dialog
snt.getPlugin().enableSnapCursor(False)
pm_ui = snt.getUI().getPathManager()

# Apply Path Manager's Tag>Image Metadata>/Morphometry commands
pm_ui.runCommand("Traced Channel")
pm_ui.runCommand("Traced Frame")
pm_ui.runCommand("Length")

# Select only "KF" paths
pm_ui.applySelectionFilter("Path order", 2)

# Run Path Manager's Analyze>Distribution Analysis... command
pm_ui.runCommand("Distribution of Path Properties...", "Node intensity values")

# Run Path Manager's Analyze>Color Coding... command
pm_ui.runCommand("Color Code Path(s)...", "X coordinates", "Cyan Hot.lut")

# Run Path Manager's Analyze>Convert to ROIs... NB: The display properties
# of the ROIs are set using ROIManager's "Properties" command
pm_ui.runCommand("Convert to ROIs...", "Tips")

# Highlight first path
pm_ui.clearSelection()
pm_ui.applySelectionFilter("Centrosome")
pm_ui.applyTag("magenta")

# Select all paths and update displays
pm_ui.selectAll()
snt.updateViewers()

