These instructions are meant to be performed in the order presented. A system Java installation is also necessary for the DiademMetric.jar to be executed with Python's subprocess module.

### Download the Olfactory Projection Fibers Dataset

1. Open http://diademchallenge.org/data_set_downloads.html
2. Download ```Olfactory_Projection_Fibers.rar```  into ```/.../FigS1_Hessian/```
3. Extract ```Olfactory_Projection_Fibers.rar``` into the same directory.

### Download the Diadem Metric

1. Open http://diademchallenge.org/metric_readme.html
2. Download ```DiademMetric.zip``` or ```Diadem Metric.tar``` into ```/.../FigS1_Hessian/```
3. Extract the archive to ```/.../FigS1_Hessian/DiademMetric/```

For more information regarding the Diadem Metric and Olfactory Projection Fibers Dataset, see:
- http://diademchallenge.org/metric.html
- http://diademchallenge.org/olfactory_projection_fibers_readme.html

At this point, the ```/.../FigS1_Hessian/``` directory structure (excluding files) should resemble:

![alt text](./misc/dirstructure.png?raw=true)

### Run generate_figure_data.py

1. From the Script Editor, go to File -> Open
2. Select ```/.../FigS1_Hessian/generate_figure_data.py``` in the file explorer.
3. Once the script is loaded in the Script Editor, press "Run" in the bottom-left corner of the editor.

In the prompt, choose the following path for the core directory:

| Field                                     | Directory               |
| ------------------------------------------| :----------------------:|
|"Directory to host all script requirements"| /.../FigS1_Hessian/ |


4. Press "OK" and allow the script to run. Note this may take several hours.

Once the script has terminated, 3 ```.CSV``` files will be present in ```/.../FigS1_Hessian/```:
- ```baseline-scores.csv``` – contains the Diadem scores for the baseline A-star group; one score for each of the 9 cells.
- ```hessian-scores.csv``` – contains the Diadem scores for the Hessian group, each of the 9 rows contains the Diadem scores for one cell over the range of sigma values.
- ```sigmas.csv``` – contains the range of sigma values used in the experiment.
