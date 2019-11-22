from sc.fiji.snt.io import (MouseLightLoader, MouseLightQuerier)
from sc.fiji.snt.annotation import (AllenCompartment, AllenUtils)
from sc.fiji.snt.analysis import TreeAnalyzer
from sc.fiji.snt.analysis.graph import GraphUtils
from org.jgrapht import Graphs
from collections import (Counter, defaultdict)
import os.path, json, math

max_ontology_level = 7
length_cutoff = 0.05
out_path = os.path.join(os.path.expanduser('~'), 'Desktop/', 'AreaCountsLength.json')

diagonal_dict = {}


def create_compartment_dict(graph):
    global max_ontology_level

    compartment_dict = defaultdict(list)
    valid_ancestor = AllenUtils.getCompartment('grey')
    for n in graph.vertexSet():
        annotation = n.getAnnotation()
        if annotation is not None:
            if not annotation.containedBy(valid_ancestor):
                continue
            depth = annotation.getOntologyDepth()
            if depth > max_ontology_level:
                annotation_ancestor = annotation.getAncestor(max_ontology_level-depth)
            else:
                annotation_ancestor = annotation
            if annotation_ancestor.isMeshAvailable():
                compartment_dict[annotation_ancestor.id()].append(n)

    return compartment_dict


def get_cable_length_by_compartment(compartment_dict, graph):

    compartment_lengths = {}
    for c in compartment_dict:
        c_nodes = compartment_dict[c]
        c_length = 0
        for n in c_nodes:
            p_list = Graphs.predecessorListOf(graph, n)
            if len(p_list) > 0:
                p = p_list[0]
                e = graph.getEdge(p, n)
                w = graph.getEdgeWeight(e)
                c_length += w
        compartment_lengths[c] = c_length

    return compartment_lengths


def filter_compartments_by_bounding_box(compartment_lengths):
    global length_cutoff
    global diagonal_dict

    filtered_compartments = []
    for c in compartment_lengths:
        if c in diagonal_dict:
            if compartment_lengths[c] >= (diagonal_dict[c] * length_cutoff):
                filtered_compartments.append(c)
            else:
                continue
        else:
            mesh = AllenCompartment(c).getMesh()
            if mesh is not None:
                diag = mesh.getBoundingBox('left').getDiagonal()
                diagonal_dict[c] = diag
                if compartment_lengths[c] >= (diag * length_cutoff):
                    filtered_compartments.append(c)
    return filtered_compartments


def run():

    if not MouseLightLoader.isDatabaseAvailable():
        print("Cannot reach ML database. Aborting...")
        return

    soma_compartment = AllenUtils.getCompartment("Whole Brain")
    trees = []
    score_dict = {}

    print("Retrieving valid identifiers. This can take several minutes...")
    for id in MouseLightQuerier.getIDs(soma_compartment):

        loader = MouseLightLoader(id)
        print("Parsing " + id + "...")

        axon = loader.getTree('axon')
        graph = GraphUtils.createGraph(axon)
        compartment_dict = create_compartment_dict(graph)
        compartment_lengths = get_cable_length_by_compartment(compartment_dict, graph)
        filtered_compartments = filter_compartments_by_bounding_box(compartment_lengths)

        axon.setLabel(axon.getLabel()[0:6])
        score_dict[axon.getLabel()] = len(filtered_compartments)

    #sorted_names = sorted(score_dict, key=lambda x: score_dict[x])
    #print(sorted_names)

    with open(outisMeshAvailable_path, 'w') as f:
        json.dump(score_dict, f)


run()
