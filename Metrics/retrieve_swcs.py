import os
import sys
from sc.fiji.snt import Tree
from sc.fiji.snt.io import MouseLightLoader

""" To be run From Fiji's script editor """

# Define output directory (where SWC files will be saved)
swc_dir = r"C:\Users\cam\Documents\repos\SNTmanuscript\Metrics\swc"
if not os.path.isdir(swc_dir):
    os.mkdir(swc_dir)


def retrieve_swcs(group_ids, group_label):
    print(group_label, len(group_ids), "reconstructions")
    group_dir = os.path.join(swc_dir, group_label)
    if not os.path.isdir(group_dir):
        os.mkdir(group_dir)
    for id_string in group_ids:
        tree = MouseLightLoader(id_string).getTree()
        swc_filepath = os.path.join(group_dir, tree.getLabel() + ".swc")
        tree.saveAsSWC(swc_filepath)

"""
Speficy three types of mouse thalamic-projecting motor neuron with differing projection patterns
described in Winnubst et al. 2019 (https://pubmed.ncbi.nlm.nih.gov/31495573/):
Layer 6 Corticothalamic neurons
Layer 5 Medulla projecting PT neurons
Layer 5 Thalamus projecting PT neurons
"""

corticothalamic = ['AA0039', 'AA0101', 'AA0103', 'AA0105', 'AA0188', 'AA0278', 'AA0390',
                   'AA0394', 'AA0406', 'AA0577', 'AA0599', 'AA0633', 'AA0650', 'AA0781', 'AA0784', 'AA0799',
                   'AA0817', 'AA0837', 'AA0838', 'AA0844']

pt_medulla = ['AA0012', 'AA0131', 'AA0133', 'AA0134', 'AA0169', 'AA0179', 'AA0180', 'AA0576',
              'AA0788', 'AA0923']

pt_thalamus = ['AA0011', 'AA0114', 'AA0115', 'AA0122', 'AA0181', 'AA0182', 'AA0245', 'AA0261',
               'AA0415', 'AA0617', 'AA0764', 'AA0780', 'AA0792', 'AA0926']

retrieve_swcs(corticothalamic, "Corticothalamic")
retrieve_swcs(pt_medulla, "PT-Medulla")
retrieve_swcs(pt_thalamus, "PT-Thalamus")
