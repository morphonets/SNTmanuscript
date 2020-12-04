#@Context context
#@LogService log
#@LUTService lut
#@SNTService snt


"""
file:	
version: 
info:	
"""

from sc.fiji.snt import Tree
from sc.fiji.snt.analysis.graph import (AnnotationGraph, GraphColorMapper, SNTPseudograph, AnnotationWeightedEdge)
from sc.fiji.snt.annotation import (AllenCompartment, AllenUtils)
from sc.fiji.snt.io import MouseLightLoader
from sc.fiji.snt.util import BoundingBox
from sc.fiji.snt.viewer import (Annotation3D, OBJMesh, GraphViewer)
from sc.fiji.snt.viewer.geditor import mxCircleLayoutGrouped
from com.mxgraph.layout import mxParallelEdgeLayout

# Documentation Resources: https://imagej.net/SNT:_Scripting
# Latest SNT API: https://morphonets.github.io/SNT/

annotation_pool = {} # global
diagonal_dict = {} # global
length_cutoff = 0.05


def filter_compartments_by_bounding_box(g):
	removed_edges = []
	for e in g.edgeSet():
		compartment = get_node(e.getTarget().id())
		diag = get_diagonal(compartment)
		if diag is None: continue
		if (e.getWeight() < diag * length_cutoff):
			removed_edges.append(e)
	g.removeAllEdges(removed_edges)
	removed_vertices = []
	for v in g.vertexSet():
		if g.degreeOf(v) == 0:
			removed_vertices.append(v)
	g.removeAllVertices(removed_vertices)


def normalize_edge_weights(g):
	max_w = float("-inf")
	min_w = float("inf")
	for e in g.edgeSet():
		if e.getWeight() > max_w:
			max_w = e.getWeight()
		if e.getWeight() < min_w:
			min_w = e.getWeight()
	for e in g.edgeSet():
		g.setEdgeWeight(e, e.getWeight() / max_w)
		
		
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
	node = annotation_pool.get(int_id)
	if node is None:
		node = AllenCompartment(int_id)
		annotation_pool[int_id] = node
	return node



for cell_id in [ "AA1044", "AA0100", "AA0788" ]:
    t = MouseLightLoader(cell_id).getTree("axon")
    g1 = AnnotationGraph([t], "tips", 2, 7)
    g2 = AnnotationGraph([t], "length", 0, 7)
  
    filter_compartments_by_bounding_box(g2)
    normalize_edge_weights(g1)
    normalize_edge_weights(g2)
 
    mapper = GraphColorMapper(context)
    mapper.setMinMax(0.10, 1.0)
    mapper.map(g1, GraphColorMapper.EDGE_WEIGHT, "mpl-plasma")
    mapper.map(g2, GraphColorMapper.EDGE_WEIGHT, "mpl-viridis")
  
    intersection_graph = merge_graphs(g1, g2)
  
    viewer = GraphViewer(intersection_graph)
    viewer.setContext(context)
    editor = viewer.getEditor()
    snt_graph_adapter = editor.getGraphComponent().getGraph()
    snt_graph_adapter.scaleEdgeWidths(1, 15, "linear")
    grouped_layout = mxCircleLayoutGrouped(snt_graph_adapter, 7, 4)
    if cell_id == "AA1044":
    	grouped_layout.setRadius(100)
    else:
    	grouped_layout.setRadius(0) # determine suitable radius automatically
	grouped_layout.setCenterSource(True)
    editor.applyLayout(grouped_layout)
    editor.applyLayout(mxParallelEdgeLayout(snt_graph_adapter))  
    viewer.show()
