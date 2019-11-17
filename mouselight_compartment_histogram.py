# @LUTService lut
# @Context context

from sc.fiji.snt.io import MouseLightLoader
from sc.fiji.snt.annotation import AllenUtils
from sc.fiji.snt.annotation import AllenCompartment
from sc.fiji.snt.analysis import TreeAnalyzer
from sc.fiji.snt.analysis.graph import GraphUtils

from org.jgrapht import Graphs

import json
from collections import Counter


def get_target_regions(nodes):
    all_targets = []
    for bp in nodes:
        annotation = bp.getAnnotation()
        if annotation is not None:
            # gets level 7 compartments...e.g. Primary somatosensory area.
            if annotation.getOntologyDepth() > 8:
                diff = 8 - annotation.getOntologyDepth()
                annotation_ancestor = annotation.getAncestors()[diff]

                # print(annotation_ancestor.name(), annotation_ancestor.getOntologyDepth())

            else:
                annotation_ancestor = annotation

            all_targets.append(str(annotation_ancestor))

    return all_targets


def filter_tips_by_terminal_length(graph_tips, graph):
    filtered_tips = []
    for t in graph_tips:
        path_length = 0
        current = t
        while True:
            if graph.outDegreeOf(current) > 1:
                break
            p = Graphs.predecessorListOf(graph, current)[0]
            e = graph.getEdge(p, current)
            w = graph.getEdgeWeight(e)
            path_length += w
            current = p
        if path_length >= 20:
            filtered_tips.append(t)

    return filtered_tips


def run():
    compartment_of_interest = AllenUtils.getCompartment("Whole Brain")

    if (not MouseLightLoader.isDatabaseAvailable()) or (compartment_of_interest is None):
        return

    trees = []
    score_dict = {}
    
    for neuron in range(1, MouseLightLoader.getNeuronCount()):

        id = "AA%04d" % neuron
        loader = MouseLightLoader(id)
        print("Parsing " + id + "...")

        if not loader.idExists():
            print("ID not found. Skipping...")
            continue

        soma = loader.getNodes("soma").toArray()[0]
        soma_compartment = soma.getAnnotation()

        if compartment_of_interest.contains(soma_compartment):
            axon = loader.getTree("axon", None)

            graph = GraphUtils.createGraph(axon)
            graph_tips = [node for node in graph.vertexSet().toArray() if graph.outDegreeOf(node) == 0]

            filtered_tips = filter_tips_by_terminal_length(graph_tips, graph)
            tip_targets = get_target_regions(filtered_tips)

            tip_counter = Counter(tip_targets)
            at_least_2_tips = [x[0] for x in tip_counter.items() if x[1] >= 2]
            
            axon.setLabel(axon.getLabel()[0:6])
            score_dict[axon.getLabel()] = len(at_least_2_tips)

    sorted_names = sorted(score_dict, key=lambda x: score_dict[x])
    print(sorted_names)

    outpath = r'C:\Users\arshadic\Desktop\compartment_counts_tips_at_least_20_um.json'
   
    with open(outpath, 'w') as f:
        json.dump(score_dict, f)


run()
