#@Context context
#@SNTService snt
from sc.fiji.snt import Tree
from sc.fiji.snt.analysis import (TreeStatistics, GroupedTreeStatistics)
from sc.fiji.snt.analysis.graph import GraphColorMapper as GCM


def showChart(chart, w, h):
    chart.setFontSize(16)
    chart.setSize(w, h)
    chart.show()

# panel a 
group1 = snt.demoTrees()[0:2]
group2 = snt.demoTrees()[2:4]
stats = GroupedTreeStatistics()
stats.addGroup(group1, "Group 1")
stats.addGroup(group2, "Group 2")
hist = stats.getHistogram("inter-node distance")
showChart(hist, 700, 750)

# panel b
tree = snt.demoTrees()[0]
stats = TreeStatistics(tree)
hist = stats.getHistogram("inter-node distance")
showChart(hist, 700, 750)

# panel c
soma_loc = tree.getRoot().getAnnotation().acronym()
hist = stats.getAnnotatedLengthHistogram()
hist.annotateCategory(soma_loc, "Soma")
showChart(hist, 400, 750)

# panel d
graph = tree.getGraph()
GCM(context).map(graph, "Edge weight", "Ice")
graph.show()
