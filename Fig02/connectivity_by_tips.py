from sc.fiji.snt.io import (MouseLightLoader, MouseLightQuerier)
from sc.fiji.snt.annotation import (AllenCompartment, AllenUtils)
from sc.fiji.snt.analysis import (TreeAnalyzer, NodeStatistics)
import os.path, json

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
        annotated_frequencies_dict = NodeStatistics(tips).getAnnotatedFrequencies(max_ontology_level)
        # Filter for relevant compartments
        annotated_frequencies_dict = {compartment: count for (compartment, count) in annotated_frequencies_dict.items()
                                      if
                                      compartment is not None
                                      and
                                      compartment.isChildOf(valid_ancestor)}

        filtered_targets_list = [compartment.name() for (compartment, count) in annotated_frequencies_dict.items()
                                 if
                                 count >= tips_cutoff]

        score_dict[id] = len(filtered_targets_list)
        print('	# targets: ' + str(score_dict[id]))

    with open(out_path, 'w') as f:
        json.dump(score_dict, f)


run()
