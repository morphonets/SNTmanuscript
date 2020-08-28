#@Context context

from sc.fiji.snt import Tree
from sc.fiji.snt.analysis import *
from sc.fiji.snt.analysis.graph import AnnotationGraph, AnnotationWeightedEdge, GraphColorMapper, SNTPseudograph
from sc.fiji.snt.annotation import AllenCompartment
from sc.fiji.snt.io import MouseLightLoader
from sc.fiji.snt.viewer import GraphViewer
from sc.fiji.snt.viewer.geditor import mxCircleLayoutGrouped


# Documentation Resources: https://imagej.net/SNT:_Scripting
# Latest SNT API: https://morphonets.github.io/SNT/


annotation_pool = {} # global

        
def build_edge_dict(g):
    edge_dict = {}
    for e in g.edgeSet():
        e_string = str(e.getSource().id()) + "," + str(e.getTarget().id())
        edge_dict[e_string] = e
    return edge_dict


def merge_graphs(g1, g2):
    edge_dict_1 = build_edge_dict(g1)
    edge_dict_2 = build_edge_dict(g2)
    intersection_keys = set(edge_dict_1.keys()) & set(edge_dict_2.keys())
    merged_graph = SNTPseudograph(AnnotationWeightedEdge)
    for edge_str in intersection_keys:
        edge_str_split = edge_str.split(',')
        source = get_node(int(edge_str_split[0]))
        target = get_node(int(edge_str_split[1]))
        if not merged_graph.containsVertex(source):
            merged_graph.addVertex(source)
        if not merged_graph.containsVertex(target):
            merged_graph.addVertex(target)
            
        new_edge = merged_graph.addEdge(source, target)
        merged_graph.setEdgeWeight(new_edge, edge_dict_1[edge_str].getWeight())
        # Use edge color from source graph
        merged_graph.setEdgeColor(new_edge, g1.getEdgeColor(edge_dict_1[edge_str]))
        
        new_edge = merged_graph.addEdge(source, target)
        merged_graph.setEdgeWeight(new_edge, edge_dict_2[edge_str].getWeight())
        # Use edge color from source graph
        merged_graph.setEdgeColor(new_edge, g2.getEdgeColor(edge_dict_2[edge_str]))
        
    return merged_graph


def get_diagonal(compartment):
    diag = diagonal_dict.get(compartment)
    if diag is None:
        mesh = compartment.getMesh()
        if mesh is None:
            return None
        diag = mesh.getBoundingBox('left').getDiagonal()
        diagonal_dict[compartment] = diag
    return diag

def get_node(int_id):
    global annotation_pool
    node = annotation_pool.get(int_id)
    if node is None:
        node = AllenCompartment(int_id)
        annotation_pool[int_id] = node
    return node

def get_trees(id_list):
    trees = []
    for i in id_list:
        t = MouseLightLoader(i).getTree("axon")
        trees.append(t)
    return trees

def show_graph(graph):

    # Color code edges (i.e., run Graph Viewer's Analyze>Color Coding... commmand)
    mapper = GraphColorMapper(context)
    mapper.setMinMax(10, 400) # 10-400 Axonal endings
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
    editor.applyLayout(grouped_layout)

    # Display result. NB: Aesthetic customizations (font size, label background,
    # position of root (somatic brain area), etc.) performed from Graph Viewer.
    # (e.g., 'Diagram>Style>Minimal Style')
    viewer.show()

def main():
    """
    Speficy the two types of mouse neurons from MOs with differing projection patterns
    described in Winnubst et al. 2019 (https://pubmed.ncbi.nlm.nih.gov/31495573/):
        med_ids:  Layer 5 Medulla projecting PT neurons 
        thal_ids: Layer 6 Corticothalamic PT neurons
    """
    med_ids = ['AA0011', 'AA0012', 'AA0115', 'AA0179', 'AA0180', 'AA0181', 'AA0182', 'AA0245', 
              'AA0250', 'AA0576', 'AA0726', 'AA0788', 'AA0791', 'AA0792']
    thal_ids = ['AA0039', 'AA0101', 'AA0103', 'AA0105', 'AA0188', 'AA0278', 'AA0390', 'AA0394', 
              'AA0406', 'AA0577', 'AA0599', 'AA0633', 'AA0650', 'AA0781', 'AA0784', 'AA0799', 
              'AA0817', 'AA0837', 'AA0838', 'AA0844']
    thal_trees = get_trees(thal_ids)
    med_trees = get_trees(med_ids)
    thal_graph = AnnotationGraph(thal_trees, "tips", 10, 6)
    med_graph = AnnotationGraph(med_trees, "tips", 10, 6)
    show_graph(thal_graph)
    show_graph(med_graph)


main()
