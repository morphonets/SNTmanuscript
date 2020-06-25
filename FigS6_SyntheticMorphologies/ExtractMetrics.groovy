#@ImageJ ij


import sc.fiji.snt.*
import sc.fiji.snt.analysis.*

// To be run from Fiji's Script Editor

def measure(path) {

    dir = new File(path)
    metrics = TreeAnalyzer.getAllMetrics()
    metrics.remove(MultiTreeStatistics.N_PATHS)
    metrics.remove(MultiTreeStatistics.N_FITTED_PATHS)
    metrics.remove(MultiTreeStatistics.ASSIGNED_VALUE)
    metrics.remove(MultiTreeStatistics.INTER_NODE_DISTANCE);

    table = new SNTTable()
    for (tree in Tree.listFromDir(path)) {
        println("Measuring "+ tree.getLabel())
        analyzer = new TreeAnalyzer(tree)
        analyzer.setContext(ij.context())
        analyzer.setTable(table, dir.getName())
        analyzer.measure(metrics, false) // will display table

        // Used GRN is included in the filename
        // e.g., snt_maxTime_6_filenameGRN_grn_0.grn_randomSeed_46944944
        // Let's store it in a dedicated column.
        label = tree.getLabel();
        table.appendToLastRow("filenameGRN", label[26..30])
    }
    table.removeColumn("SWC Types")

    table.fillEmptyCells(Double.NaN)
    table.save(new File(dir, dir.getName() + ".csv"))
}

root = "/home/tferr/SNTmanuscript/Simulations/"

measure(root + "grn0")
measure(root + "grn1")
measure(root + "grn2")
measure(root + "grn3")
