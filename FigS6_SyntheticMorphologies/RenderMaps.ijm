dir = "/home/tferr/code/morphonets/SNTmanuscript/FigS6_SyntheticMorphologies/proj/"
close("*");
files = getFileList(dir);
for (i=0; i<files.length; i++) {
	if (endsWith(files[i], ".tif")) {
    	open(dir + files[i]);
    	if ( matches(getTitle(), ".*grn2.*") || matches(getTitle(), ".*grn4.*") ) {
   			run("Size...", "width="+ 2.2 * getWidth() +" height="+ 2.2 * getHeight() 
   				+" constrain interpolation=Bicubic");
   		}
   	}
}

run("Images to Stack", "method=[Copy (center)] name=Stack title=[] use ");
open(dir + "mod-viridis.lut");
run("Make Montage...", "columns="+ nSlices() +" rows=1 scale=1 use");
run("Divide...", "value=1000.000"); // n. of files per group
setMinAndMax(0, 30);
run("Calibration Bar...", "location=[Upper Left] fill=None label=Black number=2 decimal=0 font=14 zoom=5 overlay");
close("\\Others");
