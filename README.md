# SNT Manuscript Scripts

This repository hosts the scripts that were used to assemble the figures of the [SNT publication](https://doi.org/10.1101/2020.07.13.179325).

These scripts are intended to run from a Fiji installation subscribed to the Neuroanatomy update site, as detailed in the [SNT documentation](https://imagej.net/SNT#Installation). Scripts relying on sciview/Cx3D functionality, also require the optional subscription to the *SciView-Unstable* update site. Since data is frequently downloaded from external servers, an internet connection is required.



## Download

To simplify execution, we provide ZIP files that pre-bundle an existing Fiji installation with all the required update-site subscriptions. The same ZIP file also contains the contents of this repository. **These self-contained ZIP files are provided [here](https://github.com/morphonets/SNTmanuscript/releases).** 

If instead you prefer to run these scripts on your local Fiji installation, please download the contents of this repository independently using this [direct link](https://github.com/morphonets/SNTmanuscript/archive/master.zip).



## Running a script

Each figure is associated with a sub-directory of `SNTmanuscript` (e.g., `SNTmanuscript/Fig01/`) . The sub-directory then contains one or more scripts. The majority should be run from Fiji, and  can be dragged-and-dropped into Fiji's main window: Once displayed in Fiji's script editor, they can be executed by pressing 'Run' (<kbd>CTRL</kbd>+<kbd>R</kbd>). When relevant, further details are provided on the sub-directory's `README.md` file.

Note however that some scripts (e.g., in [Metrics](./metrics) and  [FigS6](./FigS6_SyntheticMorphologies)), should be run from a Python environment. Also, please note  that not all scripts are self-contained. Some will require separate download of data (e.g., [Fig. S1](./FigS1_Hessian)). In those cases, further details are provided on the figure's `README.md` file. Please do open an [issue](https://github.com/morphonets/SNTmanuscript/issues) if you run into problems.

