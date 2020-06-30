dir = "/home/tferr/code/morphonets/SNTmanuscript/FigS6_SyntheticMorphologies/proj/"
close("*");
files = getFileList(dir);
for (i=0; i<files.length; i++) {
	if (endsWith(files[i], ".tif")) {
    	open(dir + files[i]);
   	}
}

run("Images to Stack", "method=[Copy (center)] name=Stack title=[] use ");
open(dir + "mod-viridis.lut");
run("Make Montage...", "columns="+ nSlices() +" rows=1 scale=1 use");
setMinAndMax(0, 0.20);
run("Calibration Bar...", "location=[Upper Left] fill=None label=Black number=2 decimal=2 font=14 zoom=5 overlay");
close("\\Others");
