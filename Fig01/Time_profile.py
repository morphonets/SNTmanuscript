# @SNTService snt

import os
import inspect
import sc.fiji.snt.PathManagerUI

fig_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda: 0)))
traces_file = os.path.join(fig_dir, "traces", "701.traces")

# Load files
snt.initialize(True)  # whether ui should be displayed
snt.loadTracings(traces_file)

# Apply Path Manager's Tag>Image Metadata> command
pm_ui = snt.getUI().getPathManager()
pm_ui.selectAll()
pm_ui.runCommand("Traced Frame")

# Run Path Manager's Analyze>Color Coding... command
pm_ui.runCommand("Color Code Path(s)...", "Path frame", "mpl-viridis.lut")

# Options: Metric: Cable Length; Grouping Strategy: "Matched path(s) across time";
pm_ui.runCommand("Time Profile...",)
