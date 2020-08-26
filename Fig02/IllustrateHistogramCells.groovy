#@ImageJ ij

import sc.fiji.snt.Tree
import sc.fiji.snt.analysis.TreeColorMapper
import sc.fiji.snt.io.MouseLightLoader
import sc.fiji.snt.viewer.Viewer3D
import sc.fiji.snt.viewer.OBJMesh
import sc.fiji.snt.annotation.AllenUtils


// Define output directory
dir = System.properties.'user.home' + '/Desktop/'

// Define colors of brain areas
colorMap = [:]
colorMap["MO"]   ="#803E75"
colorMap["SS"]   ="#FF6800"
colorMap["CP"]   ="#FFB300"
colorMap["TH"]   ="#F6768E"
colorMap["LHA"]  ="#007D34"
colorMap["SNr"]  ="#FF8E00"
colorMap["MB"]   ="#00538A"
colorMap["TEa"]  ="#A6BDD7"
colorMap["ECT"]  ="#C10020"
colorMap["PIR"]  ="#CEA262"
colorMap["Pons"] ="#FF7A5C"
colorMap["MY"]   ="#53377A"


// Associate brain areas to individual cells
cellMap = [:]
cellMap["AA1044"] = ["CP", "SNr"]
cellMap["AA0100"] = ["MO","SS","CP","TEa","ECT","PIR"]
cellMap["AA0788"] = ["MO","CP","TH","LHA","MB","Pons","MY"]

// Define colors/LUTs
dendritesColor = "black"
axonLut = "Ice"

// Assemble Color Mapper for axonal arbors
mapper = new TreeColorMapper(ij.context())
mapper.setMinMax(10, 20000) // assign fixed range

// Generate figure panels
cellMap.each{ id, brainAreas ->

	// Assemble viewer
	viewer = new Viewer3D(ij.context())
	viewer.setEnableDarkMode(false)
	viewer.loadRefBrain("Allen")
	viewer.show(-1, -1) // full screen

	// temporary halt scene updates
	viewer.setSceneUpdatesEnabled(false)

	// render meshes
	loadedMeshes = []
	for (area in brainAreas) {
		mesh = AllenUtils.getCompartment(area).getMesh()
		mesh.setColor(colorMap[area], (brainAreas.size() == 1) ? 95 : 97)
		viewer.addMesh(mesh)
	}
	loader = new MouseLightLoader(id)

	// Render dendrites
	dTree = loader.getTree("dendrite")
	dTree.setColor(dendritesColor)
	viewer.add(dTree)
	viewer.setTreeThickness(7, dTree.getLabel())

	// Render axon
	aTree = loader.getTree("axon")
	mapper.map(aTree, "Path distance to soma", axonLut)
	viewer.add(aTree)
	viewer.setTreeThickness(8, aTree.getLabel())
	
	// Take snapshots. NB: The bounds recorded while navigating viewer and
	// pressing 'l', Reconstruction's Viewer shortcut for 'log scene controls')
	viewer.setSceneUpdatesEnabled(false)
    viewer.validate()
	viewer.setViewMode("top");
	viewer.setBounds(3220.8774, 8590.967, 2163.2825, 5996.878, 3499.5662, 10476.271);
	viewer.saveSnapshot(dir + id + "_TOP.png")
	
	viewer.setViewMode("side")
	viewer.setBounds(1983.9384, 9391.152, 1254.8329, 6542.6924, 2176.2678, 11799.568);
	viewer.saveSnapshot(dir + id + "_SIDE.png")

	viewer.dispose()
}

return null;