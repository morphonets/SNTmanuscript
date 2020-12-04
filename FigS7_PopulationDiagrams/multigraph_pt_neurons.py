# @Context context

import os
import re
from sc.fiji.snt import Tree
from sc.fiji.snt.analysis.graph import AnnotationGraph, GraphColorMapper
from sc.fiji.snt.io import MouseLightLoader
from sc.fiji.snt.viewer import GraphViewer
from sc.fiji.snt.viewer.geditor import mxCircleLayoutGrouped


# Documentation Resources: https://imagej.net/SNT:_Scripting
# Latest SNT API: https://morphonets.github.io/SNT/


def show_graph(graph):
    # Color code edges (i.e., run Graph Viewer's Analyze>Color Coding... commmand)
    mapper = GraphColorMapper(context)
    mapper.setMinMax(10, 400)  # 10-400 Axonal endings
    mapper.map(graph, GraphColorMapper.EDGE_WEIGHT, "mpl-viridis")

    viewer = GraphViewer(graph)
    viewer.setContext(context)
    editor = viewer.getEditor()

    # Scale thickness of edges (Graph Viewer's Analyze>Scale Edge Widths... commmand)
    snt_graph_adapter = editor.getGraphComponent().getGraph()
    snt_graph_adapter.scaleEdgeWidths(1, 15, "linear")

    # Group target areas by ontology (Graph Viewer's 'Diagram>Layout>Circle (Grouped)...'
    # command
    grouped_layout = mxCircleLayoutGrouped(snt_graph_adapter, 7, 4)
    grouped_layout.setRadius(400)
    grouped_layout.setCenterSource(True)
    editor.applyLayout(grouped_layout)

    # Display result. NB: Aesthetic customizations (font size, label background,
    # position of root (somatic brain area), etc.) performed from Graph Viewer.
    # (e.g., 'Diagram>Style>Minimal Style')
    viewer.show()


def main():
    """
    Speficy three types of mouse motor neuron with differing projection patterns
    described in Winnubst et al. 2019 (https://pubmed.ncbi.nlm.nih.gov/31495573/):
    Layer 5 Medulla projecting PT neurons
    Layer 5 Thalamic projecting PT neurons
    Layer 6 Corticothalamic PT neurons
    """
    swc_dir = r"C:\Users\cam\Documents\repos\SNTmanuscript\FigS7_PopulationDiagrams\swc"
    for group_dir in os.listdir(swc_dir):
        group = []
        for swc in os.listdir(os.path.join(swc_dir, group_dir)):
            group.append(MouseLightLoader(re.sub('\.swc$', '', swc)).getTree('axon'))
        graph = AnnotationGraph(group, "tips", 10, 6)
        show_graph(graph)


main()
