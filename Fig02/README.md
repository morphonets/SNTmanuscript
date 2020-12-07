

### Fig. 2

These folder contain four scripts:

1. [connectivity_by_norm_length.py](connectivity_by_norm_length.py) generates the "Length" series of the histogram in panel a)
2. [connectivity_by_tips.py](./connectivity_by_tips.py) generates the "End-points" series of the histogram in panel a)
3. [IllustrateHistogramCells.groovy](IllustrateHistogramCells.groovy) generates panel b). The computed frequencies at time of submission are included in the [output](./output) folder.
4. [RetrieveBrainRegions.groovy](RetrieveBrainRegions.groovy) provides a list of the sampled brain areas
5. [multigraphs.py](multigraphs.py) generates the diagrams in panel c). Once displayed in _Graph Viewer_ diagrams were rendered using:
	1. _Diagram>Layout>Circle (Grouped...)_ and choosing  _radius=400; Top-level=4; Mid-level=7; Sort mid-level compartments by weight_
	2. _Diagram>Layout>Parallel Edges_



To generate panel 2C from GUI (i.e., to perform the instructions [multigraphs.py](multigraphs.py) on the GUI), please follow the following steps:

1. Open Reconstruction Viewer: (In Fiji: *Plugins>Neuroanatomy>Reconstruction Viewer*)
2. In the newly *RV Controls* window, click on the *Neuronal Arbors* button and choose *Load from Databse>MouseLight...*, typing in the Id of the cell, e.g. `AA0100`. You may want to restrict the import to the axonal arbor only
3. Wait for the neuron to load, and choose *Create Annotation Graph...* from the *Measure* button (NB: If you have many cells loaded, select the cell imported in the objects list to ensure the command does not take into account other cells)
4. Type in the following settings:
   - Metric: `tips`
   - Threshold: `2`
   - Depth: `7`
   - Compartment: `Axon`

5. Wait for the diagram to open in *Graph Viewer*. Then customize it by:

   1. Running *Analyze>Color Coding...* with the following parameters:
      - Color by: `Edge weight`
      - LUT: `mpl-viridis.lut`
      - Use clipping range: `unchecked`
      - Show legend: `checked`
   2. Running *Analyze>Scale Edge Widths...*
      - Limits: `1-20`
   3. Running *Diagram>Layout>Circle (Grouped)...*:
      - Radius: `600` (Depending on your preference (screen size, etc.))
      - Top level: `3`
      - Mid Level: 7
      - Sort mid-level: `checked`
      - Color by group: `unchecked` (Depending on your preference, unchecked for look of panel c))
      - Move source to center: `checked`
6. Repeat procedure to other cells.