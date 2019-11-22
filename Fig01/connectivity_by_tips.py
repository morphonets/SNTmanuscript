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
    valid_ancestor = AllenUtils.getCompartment('grey')
    score_dict = {}

    print("Retrieving valid identifiers. This can take several minutes...")
    for id in MouseLightQuerier.getIDs(soma_compartment):

        loader = MouseLightLoader(id)
        print("Parsing " + id + "...")

        axon = loader.getTree('axon')
        tips = TreeAnalyzer(axon).getTips()
        targets = []
        for tip in tips:
            annotation = tip.getAnnotation()
            if annotation is None:
                continue
            if not annotation.containedBy(valid_ancestor):
                continue
            depth = annotation.getOntologyDepth()
            if depth > max_ontology_level:
                adjusted_annotation = annotation.getAncestor(max_ontology_level-depth)
            else:
                adjusted_annotation = annotation
            if not adjusted_annotation.isMeshAvailable():
                continue
            targets.append(str(adjusted_annotation))

        c = Counter(targets)
        filtered_targets = [x[0] for x in c.items() if x[1] >= tips_cutoff]
        score_dict[id] = len(filtered_targets)
        print('    # targets: ' + str(score_dict[id]))

    #sorted_names = sorted(score_dict, key=lambda x: score_dict[x])
    #print(sorted_names)

    with open(out_path, 'w') as f:
        json.dump(score_dict, f)


run()
