from sc.fiji.snt.io import (MouseLightLoader, MouseLightQuerier)
from sc.fiji.snt.annotation import (AllenCompartment, AllenUtils)
from sc.fiji.snt.analysis import TreeAnalyzer, TreeStatistics
from sc.fiji.snt.analysis.graph import GraphUtils
from org.jgrapht import Graphs
from collections import (Counter, defaultdict)
import os.path, json, math

max_ontology_level = 7
length_cutoff = 0.05
out_path = os.path.join(os.path.expanduser('~'), 'Desktop/', 'AreaCountsLength.json')

diagonal_dict = {}


def filter_compartments_by_bounding_box(compartment_length_dict):
    filtered_compartments_list = []
    for c, c_length in compartment_length_dict.items():
        if c in diagonal_dict:
            if c_length >= (diagonal_dict[c] * length_cutoff):
                filtered_compartments_list.append(c)
            else:
                continue
        else:
            mesh = c.getMesh()
            if mesh is not None:
                diag = mesh.getBoundingBox('left').getDiagonal()
                diagonal_dict[c] = diag
                if c_length >= (diag * length_cutoff):
                    filtered_compartments_list.append(c)
    return filtered_compartments_list


def run():
    if not MouseLightLoader.isDatabaseAvailable():
        print("Cannot reach ML database. Aborting...")
        return

    soma_compartment = AllenUtils.getCompartment("Whole Brain")
    valid_ancestor = AllenUtils.getCompartment('grey')
    score_dict = {}

    print("Retrieving valid identifiers. This can take several minutes...")
    for id in MouseLightQuerier.getIDs(soma_compartment):
        loader = MouseLightLoader(id)
        print("Parsing " + id + "...")

        axon = loader.getTree('axon')
        t_stats = TreeStatistics(axon)
        compartment_length_dict = t_stats.getAnnotatedLength(max_ontology_level)
        # Filter for relevant compartments with an associated mesh (needed for bounding box calculation)
        compartment_length_dict = {compartment: length for (compartment, length) in compartment_length_dict.items()
                                   if
                                   compartment is not None
                                   and
                                   compartment.isChildOf(valid_ancestor)
                                   and
                                   compartment.isMeshAvailable()}

        filtered_compartments_list = filter_compartments_by_bounding_box(compartment_length_dict)

        axon.setLabel(axon.getLabel()[0:6])
        score_dict[axon.getLabel()] = len(filtered_compartments_list)

    with open(out_path, 'w') as f:
        json.dump(score_dict, f)


run()
