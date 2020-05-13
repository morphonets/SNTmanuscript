from sc.fiji.snt.io import (MouseLightLoader, MouseLightQuerier)
from sc.fiji.snt.annotation import (AllenCompartment, AllenUtils)
from sc.fiji.snt.analysis import TreeAnalyzer
from collections import (Counter, defaultdict)
import os.path, json, math

max_ontology_level = 7
tips_cutoff = 2
out_path = os.path.join(os.path.expanduser('~'), 'Desktop/', 'AreaCountsTips.json')


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
        analyzer = TreeAnalyzer(axon)
        annotations = analyzer.getAnnotations(max_ontology_level)
        filtered_targets = []
        for compartment in annotations:
            compartment_tips = analyzer.getTips(compartment)
            if len(compartment_tips) >= tips_cutoff:
                filtered_targets.append(compartment.name())

        score_dict[id] = len(filtered_targets)
        print('    # targets: ' + str(score_dict[id]))

    with open(out_path, 'w') as f:
        json.dump(score_dict, f)


run()
