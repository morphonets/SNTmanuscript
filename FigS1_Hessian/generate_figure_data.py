# @File(label="Directory containing generate_figure_data.py", style="directory") core_directory
# @LogService log
# @SNTService snt
# @UIService ui

"""
file:       generate_figure_data.py
author:     Cameron Arshadi, Tiago Ferreira
info:       Generates Diadem scoring data for FigS1_Hessian
"""

import os
import shutil
import re
import csv
import time
from subprocess import Popen, PIPE, STDOUT

from ij.plugin import FolderOpener
from ij.measure import Calibration

from sc.fiji.snt import (Path, SNT, Tree)


def prepare_image_stacks(image_dir):
    """ For each stack directory in image_dir, load the image sequence as
    a stack and spatially calibrate the stack.

    Returns:
        images (list): The list containing the calibrated image stacks.

    Args:
        image_dir (str): The directory containing the image stack directories.
    """

    images = []
    for stack_dir in os.listdir(image_dir):
        stack_dir_full_path = str(image_dir) + '/' + stack_dir
        imp = FolderOpener.open(stack_dir_full_path)
        cal = Calibration()
        cal.setUnit('um')
        cal.pixelWidth = 0.3296485
        cal.pixelHeight = 0.3296485
        cal.pixelDepth = 0.998834955
        imp.setCalibration(cal)
        imp.setTitle(stack_dir)  # name the image after its directory, e.g. OP_1
        images.append(imp)

    return images


def prepare_gold_standard_trees(swc_dir):
    """ Scales each Gold Standard SWC by the spatial calibration of its corresponding image.
    This is necessary since the Gold Standard images are represented in pixel coordinates,
    whereas the images are calibrated in micrometers.

    Returns:
        trees (list): The list containing each scaled Gold Standard Tree
        scaled_gs_dir (str): The directory hosting the scaled Gold Standard SWCs.

    Args:
        swc_dir (str): The directory hosting the un-scaled Gold Standard SWCs.
    """

    gold_standard_swc_files = get_files(swc_dir)

    # Remove the output directory if it already exists
    # and create a new one.
    scaled_gs_dir = swc_dir + "/scaled_gs"
    if os.path.exists(scaled_gs_dir):
        shutil.rmtree(scaled_gs_dir)

    os.mkdir(scaled_gs_dir)

    trees = []
    for swc in gold_standard_swc_files:
        # Get an SNT Tree object from the SWC filepath.
        gold_standard_tree = Tree(swc)
        # Give the Tree the same label as its corresponding image.
        old_name = gold_standard_tree.getLabel()  # OP_1.swc
        new_name = old_name.replace('.swc', '')  # e.g., OP_1
        gold_standard_tree.setLabel(new_name)
        # Scale the Tree by the spatial calibration of the images.
        # This is necessary since the Gold Standard SWCs are represented in pixel coordinates.
        gold_standard_tree.scale(0.3296485, 0.3296485, 0.998834955)
        scaled_gs_filepath = scaled_gs_dir + "/{}_scaled.swc".format(new_name)
        gold_standard_tree.saveAsSWC(scaled_gs_filepath)
        trees.append(gold_standard_tree)

    return trees, scaled_gs_dir


def get_files(dir):
    """ Return a list of filepaths in dir..

    Args: dir (str): The input directory.
    """

    files = []
    for f in os.listdir(dir):
        f_path = dir + '/' + f
        if os.path.isfile(f_path):
            files.append(f_path)

    return files


def prepare_output_dir(dir):
    """ Creates the directory tree where auto-trace results will be stored,
    first removing it if it already exists.

    Args:
        dir (str): The directory to store auto-trace results.
    """

    if not os.path.isdir(dir):
        os.mkdir(dir)
    else:
        shutil.rmtree(dir)
        os.mkdir(dir)

    for i in range(1, 10):
        new_dir = dir + '/' + "Results_OP_{}".format(i)
        baseline_dir = new_dir + '/' + 'Baseline'
        hessian_dir = new_dir + '/' + 'Hessian'
        os.mkdir(new_dir)
        os.mkdir(baseline_dir)
        os.mkdir(hessian_dir)


def auto_trace(image, ref_tree, sigma, maximum, use_hessian, out_dir):
    """ For each Path in the Gold Standard Tree, perform
    A-star search between the starting and terminal points of the path
    and store the auto-traced Path in a new Tree. The resulting Tree
    is saved to the output directory.

    It is assumed that the image and ref_tree have the same spatial calibration.

    Args:
        image (ImagePlus): The image stack.
        ref_tree (Tree): Gold Standard Tree.
        sigma (float): Hessian analysis 'Sigma' parameter.
        maximum (float): Hessian analysis 'Max' parameter.
        use_hessian (bool): Whether or not to use Hessian Analysis.
        out_dir (str): The directory where the auto-traced SWCs will be stored.
    """

    # Prepare plugin for auto-tracing
    plugin = snt.initialize(image, False)  # Image stack, whether ui should be displayed.
    plugin.enableAstar(True)

    if use_hessian:
        plugin.startHessian("primary", sigma, maximum, True)  # Wait for thread to complete.

    new_tree = Tree()  # Tree which will contain the auto-traced Paths.

    for path in ref_tree.list():
        end_point = path.getNode(path.size() - 1)

        if path.getStartJoinsPoint() is None:
            # First, trace the primary Path (i.e., the Path which contains the root node).
            start_point = path.getNode(0)
            primary_path = plugin.autoTrace(start_point, end_point, None)  # A-star search between start and end point.
            new_tree.add(primary_path)

        else:
            # To trace an auxiliary Path, we first need to determine which node
            # on the previously traced Path to fork from.
            # First, find the Path and node where the current reference Path joins to the reference Tree.
            ref_tree_fork_point = path.getStartJoinsPoint()
            # Get the index of this reference Path which contains the fork point.
            ref_tree_fork_path_id = path.getStartJoins().getID()
            # Get the corresponding Path on the new Tree , since the index is the same.
            new_tree_fork_path = new_tree.get(ref_tree_fork_path_id)
            # Since the node coordinates on the new Tree will not correspond exactly to those in the reference Tree,
            # we need to find the closest corresponding node in the new Tree to the fork point on the reference Tree.
            closest_index = new_tree_fork_path.indexNearestTo(ref_tree_fork_point.x, ref_tree_fork_point.y,
                                                              ref_tree_fork_point.z, float('inf'))
            # This best candidate will be our fork point.
            new_tree_fork_point = new_tree_fork_path.getNode(closest_index)
            # A-star path tracing between the fork point and the endpoint of the current path.
            child = plugin.autoTrace([new_tree_fork_point, end_point], new_tree_fork_point)
            # Add the result to the new Tree.
            new_tree.add(child)

    cell_number = int(image.getTitle()[-1])

    # Determine where to save the traced result.
    if use_hessian:
        traced_result = str(out_dir) + "/Results_OP_{}/Hessian/OP_{}_auto-sigma-{}-.swc".format(cell_number,
                                                                                                cell_number, sigma)
    else:
        traced_result = str(out_dir) + "/Results_OP_{}/Baseline/OP_{}_auto-baseline.swc".format(cell_number,
                                                                                                cell_number)

    new_tree.setSWCType("axon")

    success = "File saved" if new_tree.saveAsSWC(traced_result) else "unsaved result. I/O error?"
    print(success)

    snt.dispose()


def diadem(metric_jar_path, gold_standard, auto_traced, hessian=False):
    """ Executes the Diadem Metric JAR as a child program in a new process.
    The Diadem score for the pair of reconstructions is taken from the output stream.

    Returns:
        (sigma, score) (tuple) if hessian == True.
        (None, score) (tuple) if hessian == False

    Args:
        metric_jar_path (str): The path of the Diadem Metric .JAR file.
        gold_standard (str): The filepath to the Gold Standard SWC.
        auto_traced (str): The filepath to the auto_traced SWC.
        hessian (bool): Whether or not to capture the sigma parameter from the auto_traced SWC filepath.
    """

    p = Popen(['java', '-jar', metric_jar_path, '-G', gold_standard, '-T', auto_traced], stdout=PIPE, stderr=STDOUT)

    for line in p.stdout:
        score = float(line.strip().split()[1])

    if hessian:
        # Capture the sigma parameter from the SWC filename
        stripped = auto_traced.strip()
        m = re.search('sigma-(.+?)-', stripped)
        if m:
            sigma = float(m.group(1))
            return (sigma, score)

        else:
            raise ValueError('No sigma captured for Hessian group tracing.')

    else:
        # If not using the Hessian analysis, there is no sigma.
        return (None, score)


def get_diadem_scores(metric_jar_path, gold_standard_dir, autotrace_dir, diadem_scores_dir):

    # Get the filepaths of the scaled Gold Standard SWCs
    gold_standards = []
    for gs in sorted(os.listdir(gold_standard_dir), key=lambda x: x[3]):
        gold_standards.append(gold_standard_dir + '/' + gs)

    """ Walk through the "OP_Autotrace_Results" directory and run the Diadem Metric for each auto-traced SWC against 
    its corresponding Gold Standard SWC. 
    
    For the baseline group, the single Diadem score for each of the 9 cell reconstructions is appended to 
    baseline_scores (list). 
    
    For each cell in the Hessian group, the Diadem score for each value of sigma is appended to cell_scores (list). 
    Then, each of these lists is appended to all_hessian_scores (list).
    """

    """ The baseline_scores list will resemble:
    [(None, score_OP_1), (None, score_OP_2), (None, score_OP_3), ... , (None, score_OP_9)]
    """

    """ The all_scores list will resemble:
    [[(sigma_1, score_1), (sigma_2, score_2), (sigma_3, score_3), ... , (sigma_n, score_n)], # OP_1
     [(sigma_1, score_1), (sigma_2, score_2), (sigma_3, score_3), ... , (sigma_n, score_n)], # OP_2
     [(sigma_1, score_1), (sigma_2, score_2), (sigma_3, score_3), ... , (sigma_n, score_n)], # OP_3
     .
     .
     .
     [(sigma_1, score_1), (sigma_2, score_2), (sigma_3, score_3), ... , (sigma_n, score_n)]] # OP_9
    """

    baseline_scores = []
    all_hessian_scores = []
    count = 0
    for root, dirs, files in os.walk(autotrace_dir):

        dirs.sort(key=lambda x: x[-1])

        if root.endswith("Baseline"):
            # Get the (single) Diadem score for each cell in the baseline group.
            for f in files:
                autotraced_swc = root + '/' + f
                pair = diadem(metric_jar_path, gold_standards[count], autotraced_swc, hessian=False)
                # only capture the score, ignoring sigma since it equals None.
                baseline_scores.append(pair[1])

        elif root.endswith('Hessian'):
            # Get the (multiple) Diadem scores for each cell in the Hessian group.
            cell_scores = []
            for f in files:
                autotraced_swc = root + '/' + f
                pair = diadem(metric_jar_path, gold_standards[count], autotraced_swc, hessian=True)
                cell_scores.append(pair)

            # Sort the Hessian group (sigma, score) pairs by sigma, in increasing order
            # since this is our independent variable.
            cell_scores = sorted(cell_scores, key=lambda x: x[0])
            # Append the results for one cell to the list containing
            # the results for all cells.
            all_hessian_scores.append(cell_scores)

            count += 1

    # Separate the (sigma,score) pairs for each cell in the Hessian group into two lists.
    # One list of lists containing the range of scores for each reconstructed cell.
    # A single list containing the range of sigma values (which are the same for all cells).
    scores_array = []
    for l in all_hessian_scores:
        just_sigmas = [s[0] for s in l]
        just_scores = [s[1] for s in l]
        scores_array.append(just_scores)

    # Write the scores from the Hessian group to csv.
    hessian_scores_filepath = str(diadem_scores_dir) + '/hessian-scores.csv'
    with open(hessian_scores_filepath, "w") as f:
        writer = csv.writer(f)
        writer.writerows(scores_array)

    # Write the scores from the baseline A-star group to csv.
    baseline_scores_filepath = str(diadem_scores_dir) + '/baseline-scores.csv'
    with open(baseline_scores_filepath, "w") as f:
        writer = csv.writer(f)
        writer.writerow(baseline_scores)

    # Write the row of sigma values to csv.
    sigmas_filepath = str(diadem_scores_dir) + '/sigmas.csv'
    with open(sigmas_filepath, "w") as f:
        writer = csv.writer(f)
        writer.writerow(just_sigmas)


def run():

    # Exit if SNT is already busy doing something
    if snt.isActive() and snt.getUI():
        ui.showDialog("Please close SNT before calling this function. It is recommended to restart Fiji before"
                      "running this script.", "Error")
        return

    image_dir = str(core_directory) + '/Olfactory Projection Fibers/Image Stacks'
    if not os.path.isdir(image_dir):
        print('Directory containing image stacks not found. Please ensure the directory structure is correct.')
        return

    swc_dir = str(core_directory) + '/Olfactory Projection Fibers/Gold Standard Reconstructions'
    if not os.path.isdir(swc_dir):
        print('Directory containing Gold Standard SWCs not found. Please ensure the directory structure is correct.')
        return

    metric_jar_path = str(core_directory) + '/DiademMetric/DiademMetric.jar'
    if not os.path.isfile(metric_jar_path):
        print('Diadem Metric .JAR not found. Please ensure the directory structure is correct.')
        return

    output_dir = str(core_directory) + '/OP_Autotrace_Results'
    prepare_output_dir(output_dir)

    images = prepare_image_stacks(image_dir)

    gold_standard_trees, scaled_gs_dir = prepare_gold_standard_trees(swc_dir)

    # sort the lists by cell number
    images.sort(key=lambda x: x.getTitle()[-1])
    gold_standard_trees.sort(key=lambda x: x.getLabel()[-1])

    # Hand-picked values for the Hessian analysis "Maximum" parameter.
    # These are the default values that were given when choosing the Hessian parameters
    # visually in the GUI. The representative regions for the images were all
    # chosen to have significant branching with a high signal-to-noise ratio.
    # Ordered by ascending cell number, i.e., OP_1, OP_2 ... OP_9
    maxes = [17.695, 17.969, 9.12, 16.304, 8.376, 12.809, 11.697, 13.86, 10.038]

    images_trees_maxes = zip(images, gold_standard_trees, maxes)

    sigmas = []
    s = 0.1
    while s < 2.0:
        sigmas.append(s)
        s += 0.02

    iterations = len(sigmas) * 9
    count = 1
    for im, gs, ma in images_trees_maxes:

        if str(im.getTitle()) != str(gs.getLabel()):
            log.error('Image: {} and Gold Standard SWC: {} do not correspond. Exiting.'.format(str(im.getTitle()),
                                                                                               str(gs.getLabel())))
            return

        # First trace without the Hessian analysis.
        im_copy = im.duplicate()
        rename = im_copy.getTitle()[4::]  # Duplicated images are given a 'DUP_' prefix by ImageJ.
        im_copy.setTitle(rename)

        auto_trace(image=im_copy, ref_tree=gs, sigma=None, maximum=None, use_hessian=False, out_dir=output_dir)

        # Then, trace using Hessian analysis while varying the sigma parameter on each iteration.
        for si in sigmas:
            im_copy = im.duplicate()
            rename = im_copy.getTitle()[4::]
            im_copy.setTitle(rename)
            auto_trace(image=im_copy, ref_tree=gs, sigma=si, maximum=ma, use_hessian=True, out_dir=output_dir)
            print("Iteration {} / {}".format(count, iterations))
            count += 1

    get_diadem_scores(metric_jar_path, scaled_gs_dir, output_dir, core_directory)

    print("Completed.")


run()
