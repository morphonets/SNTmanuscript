### Fig S6



This data was generated from multiple resources:

1. GRNs: Generated using Cx3D's [GenerateGRNs](https://github.com/morphonets/cx3d/blob/master/src/main/java/sc/iview/cx3d/simulations/grn/GenerateGRNs.java)
2. Generation of morphologies: [run_simulations_simple.py](./run_simulations_simple.py) . The script assumes sciview and Cx3D to be available locally ([instructions](https://imagej.net/SNT#Installation)), since morphologies are actually generated in Cx3D using [GRNBranchingSWC](https://github.com/morphonets/cx3d/blob/master/src/main/java/sc/iview/cx3d/commands/GRNBranchingSWC.java)
3. Extraction of metrics: [ExtractMetrics.groovy](./ExtractMetrics.groovy)
4. Statistical analysis: [analysis.py](./analysis.py)
5.  Density maps: Generated using [DensityPlot2DTest](https://github.com/morphonets/SNT/blob/master/src/test/java/sc/fiji/snt/DensityPlot2DTest.java). Montage of projections generated using [RenderMaps](./RenderMaps.ijm)
6. Exemplars: Generated using [render_exemplars](./render_exemplars.py)



NB:

- Some of the code above uses hardwired paths. Please change them accordingly
- GRNs used in the manuscript are made available in [grn/](./grn). These can be inspected using [grneat](https://github.com/brevis-us/grneat) 
- Retrieved metrics are included in  [csv/](./csv)
- The 5,000 morphologies account for more than 300MB of data and were not included in this repository, but exemplars are included in [swc/](./swc)

