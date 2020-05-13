from sc.fiji.snt.io import (MouseLightLoader, MouseLightQuerier)
from sc.fiji.snt.annotation import (AllenCompartment, AllenUtils)
from sc.fiji.snt.analysis import TreeAnalyzer, TreeStatistics
from sc.fiji.snt.analysis.graph import GraphUtils
from org.jgrapht import Graphs
from collections import (Counter, defaultdict)
import os.path, json, math

max_ontology_level = 7
length_cutoff = 0.05
out_path = os.path.join(os.path.expanduser('~'), 'Desktop/', 'AreaCountsLength-new.json')

diagonal_dict = {}


def filter_compartments_by_bounding_box(compartment_lengths):

    filtered_compartments = []
    for c in compartment_lengths:
        if c in diagonal_dict:
            if compartment_lengths[c] >= (diagonal_dict[c] * length_cutoff):
                filtered_compartments.append(c)
            else:
                continue
        else:
            mesh = c.getMesh()
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
    score_dict = {}

    print("Retrieving valid identifiers. This can take several minutes...")
    for id in MouseLightQuerier.getIDs(soma_compartment):

        loader = MouseLightLoader(id)
        print("Parsing " + id + "...")

        axon = loader.getTree('axon')
        t_stats = TreeStatistics(axon)
        compartment_lengths = t_stats.getAnnotatedLength(max_ontology_level)
        # Discard cable not associated with any compartment
        compartment_lengths = {k: v for (k, v) in compartment_lengths.items() if k is not None}
        # Only consider compartments with an associated mesh (needed for the bounding box calculation)
        compartment_lengths = {k: v for (k, v) in compartment_lengths.items() if k.isMeshAvailable()}
        filtered_compartments = filter_compartments_by_bounding_box(compartment_lengths)

        axon.setLabel(axon.getLabel()[0:6])
        score_dict[axon.getLabel()] = len(filtered_compartments)

    with open(out_path, 'w') as f:
        json.dump(score_dict, f)


run()
