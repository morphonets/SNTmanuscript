#@ImageJ ij


import sc.fiji.snt.*
import sc.fiji.snt.analysis.*

// To be run from Fiji's Script Editor

def measure(path, group, csvDir) {

	dir = new File(path + group)
	csvDir = new File(csvDir)
	metrics = TreeAnalyzer.getAllMetrics()

	// Exlude metrics not relevant for MouseLight neurons
	metrics.remove(MultiTreeStatistics.N_PATHS)
	metrics.remove(MultiTreeStatistics.N_FITTED_PATHS)
	metrics.remove(MultiTreeStatistics.ASSIGNED_VALUE)
	metrics.remove(MultiTreeStatistics.INTER_NODE_DISTANCE);
	metrics.remove(MultiTreeStatistics.MEAN_RADIUS);

	table = new SNTTable()
	for (tree in Tree.listFromDir(path + group)) {
		println("Measuring "+ tree.getLabel())
		analyzer = new TreeAnalyzer(tree)
		analyzer.setContext(ij.context())
		analyzer.setTable(table, dir.getName())
		analyzer.measure(metrics, false) // will display table

		label = tree.getLabel();
		table.appendToLastRow("projectionGroup", group)
	}
	table.removeColumn("SWC Types")

	table.fillEmptyCells(Double.NaN)
	table.save(new File(csvDir, dir.getName() + ".csv"))
}

// Define input directory (containing SWC files)
swcDir = "C:\\Users\\cam\\Documents\\repos\\SNTmanuscript\\Metrics\\swc\\"

// Define output directory (where CSV files will be saved)
csvDir = "C:\\Users\\cam\\Documents\\repos\\SNTmanuscript\\Metrics\\csv\\"

measure(swcDir, "Corticothalamic", csvDir)
measure(swcDir, "PT-Medulla", csvDir)
measure(swcDir, "PT-Thalamus", csvDir)
