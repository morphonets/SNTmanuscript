

### Fig. 2

These folder contain four scripts:

1. [connectivity_by_norm_length.py](connectivity_by_norm_length.py) generates the "Length" series of the histogram in panel a)
2. [connectivity_by_tips.py](./connectivity_by_tips.py) generates the "End-points" series of the histogram in panel a)
3. [IllustrateHistogramCells.groovy](IllustrateHistogramCells.groovy) generates panel b). The computed frequencies at time of submission are included in the [output](./output) folder.
4. [RetrieveBrainRegions.groovy](RetrieveBrainRegions.groovy) provides a list of the sampled brain areas
5. [multigraphs.py](multigraphs.py) generates the diagrams in panel c). Once displayed in _Graph Viewer_ diagrams were rendered using:
	1. _Diagram>Layout>Circle (Grouped...)_ and choosing  _radius=400; Top-level=4; Mid-level=7; Sort mid-level compartments by weight_
	2. _Diagram>Layout>Parallel Edges_

