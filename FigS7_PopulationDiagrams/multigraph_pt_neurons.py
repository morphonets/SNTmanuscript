# @Context context

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
    Speficy two types of mouse thalamic-projecting motor neuron with differing projection patterns
    described in Winnubst et al. 2019 (https://pubmed.ncbi.nlm.nih.gov/31495573/):
    Layer 5 Medulla projecting PT neurons
    Layer 6 Corticothalamic neurons
    """

    med_ids = ['AA0011', 'AA0012', 'AA0115', 'AA0179', 'AA0180', 'AA0181', 'AA0182', 'AA0245',
              'AA0250', 'AA0576', 'AA0726', 'AA0788', 'AA0791', 'AA0792']

    thal_ids = ['AA0039', 'AA0101', 'AA0103', 'AA0105', 'AA0188', 'AA0278', 'AA0390', 'AA0394',
              'AA0406', 'AA0577', 'AA0599', 'AA0633', 'AA0650', 'AA0781', 'AA0784', 'AA0799',
              'AA0817', 'AA0837', 'AA0838', 'AA0844']

    all_groups = [med_ids, thal_ids]

    for group_ids in all_groups:
        group_trees = []
        for id_string in group_ids:
            group_trees.append(MouseLightLoader(id_string).getTree('axon'))
        graph = AnnotationGraph(group_trees, "tips", 10, 6)
        show_graph(graph)


main()
