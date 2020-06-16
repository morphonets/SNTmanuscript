# %%
import sys
import os
!conda install --yes --prefix {sys.prefix} -c conda-forge pyimagej openjdk=8 scipy
# %%
import imagej
import numpy as np
#import svgwrite
from fpdf import FPDF
# %%
# Initialize Fiji with GUI support.

from os.path import expanduser
home = expanduser("~")

#result_directory = home + '/Dropbox/SNTmanuscript/Simulations/GRNFinalAnalysis/'
result_directory = home + '/Data/SNT/GRN_RandomNeuriteDir/'
output_directory = result_directory + '/output/'

num_grns = 5

# %%
# Get the Cx3D data

import pandas as pd

data = {}

for grn in range(num_grns):
    filename = result_directory + 'grn_' + str(grn) + '.csv'
    pdata = pd.read_csv(filename, sep='\t')
    data[filename] = pdata


pdata = pd.concat(data.values())

# %%

# Keys for SNT measurements
snt_keys = [k for k in pdata.keys() if k != 'UIDrandomSeed' and k != 'filenameGRN' and k != 'randomSeed']

grns = sorted(list(set(pdata['filenameGRN'])))
# Dictionary that maps grn filenames to an integer GRN uid
grn_dict = dict(zip(grns, range(len(grns))))

# Filter SNT_keys
#snt_keys = ['Cable length', 'No. of terminal branches', 'No. of branch points', 'Depth', 'Horton-Strahler number', 'Horton-Strahler bifurcation ratio', 'Length of primary branches (sum)', 'Height', 'Length of terminal branches (sum)', 'No. of tips', 'No. of branches', 'Width' ]
snt_keys = ['Cable length', 'No. of branch points', 'Depth', 'Horton-Strahler number', 'No. of tips', 'No. of branches' ]
#snt_keys = ['Cable length', 'Width', 'Depth', 'Horton-Strahler bifurcation ratio', 'Height']
#snt_keys = ['Width', 'Depth', 'Height']

# Matrix of SNT measurements
snt_mat = pdata.as_matrix(columns=snt_keys)
# Matrix of GRN uids
grn_mat = np.array([ grn_dict[grn] for grn in pdata['filenameGRN'] ])

# Remove all entries with nan's
#nan_mask = [ 1 if v else 0 for v in ~np.isnan(snt_mat).any(axis=1) ]
nan_mask = ~np.isnan(snt_mat).any(axis=1)
grn_mat = grn_mat[nan_mask]
snt_mat = snt_mat[nan_mask]# remove from snt_mat last

from sklearn import preprocessing
norm_snt_mat = preprocessing.normalize(snt_mat)


print(grn_mat.shape)
print(snt_mat.shape)

full_mat = np.hstack([grn_mat[:,np.newaxis], snt_mat])

print(snt_mat[0,:])

#data.dtype.names

snt_keys

# %%

results = {}

# First find all lineages that we actually have
for k in list(grn_dict.keys()):
    parts = k.split('_')
    grn = int(parts[1].split('.')[0])
    if grn in results:
        results[grn] = sorted( results[grn] + [k] )
    else:
        results[grn] = [k]

# Now make a dict of indices
result_idx = {}
for grn in results:
    vs = []
    for grnfile in results[grn]:
        vs += [grn_dict[grnfile]]
    result_idx[grn] = vs

# Lineages now is a sorted list of GRN indices, sort is small to large of grn distance
results

# %%
# Pair plots

import matplotlib.pyplot as plt
import pandas as pd

# Seaborn visualization library
import seaborn as sns
# Create the default pairplot

# plt.figure()
# sns.pairplot(pd.DataFrame(data=full_mat,columns=['grn']+snt_keys))
# plt.savefig(output_directory + "/pairplot_v01.png")

###
# %% Show statistical test for difference between all GRNs with a T-test

grn_a_id = 0
grn_b_id = 1

def ttest_grns(grn_a_id, grn_b_id):

    grn_a_mask = np.array([ True if grn == grn_a_id else False for grn in grn_mat ])
    grn_b_mask = np.array([ True if grn == grn_b_id else False for grn in grn_mat ])

    snt_mat_a = snt_mat[grn_a_mask,:]
    snt_mat_b = snt_mat[grn_b_mask,:]

    from scipy.spatial.distance import cdist

    mean_a = np.mean(snt_mat_a, axis=0)
    #print(mean_a[:,np.newaxis].shape)
    #print(snt_mat_a.shape)
    mean_a_dists = cdist(snt_mat_a, mean_a[np.newaxis,:])
    #print(mean_a_dists.shape)

    mean_b = np.mean(snt_mat_b, axis=0)
    mean_b_dists = cdist(snt_mat_b, mean_b[np.newaxis,:])

    from scipy import stats
    #stats.ttest_ind(snt_mat_a,snt_mat_b, equal_var = False)
    return stats.ttest_ind(mean_a_dists,mean_b_dists, equal_var = False)

for a in range(5):
    for b in range(5):
        tresult = ttest_grns(a,b)
        print([a,b,tresult])

###
# %% Show statistical test for difference between all GRNs with a KS 2 samp test

grn_a_id = 0
grn_b_id = 1

def ks2samp_grns(grn_a_id, grn_b_id):

    grn_a_mask = np.array([ True if grn == grn_a_id else False for grn in grn_mat ])
    grn_b_mask = np.array([ True if grn == grn_b_id else False for grn in grn_mat ])

    snt_mat_a = snt_mat[grn_a_mask,:]
    snt_mat_b = snt_mat[grn_b_mask,:]

    from scipy.spatial.distance import cdist

    mean_a = np.mean(snt_mat_a, axis=0)
    #print(mean_a[:,np.newaxis].shape)
    #print(snt_mat_a.shape)
    mean_a_dists = cdist(snt_mat_a, mean_a[np.newaxis,:])
    #print(mean_a_dists.shape)

    mean_b = np.mean(snt_mat_b, axis=0)
    mean_b_dists = cdist(snt_mat_b, mean_b[np.newaxis,:])

    from scipy import stats
    #stats.ttest_ind(snt_mat_a,snt_mat_b, equal_var = False)

    # compute pvalues for each dimension using ks_2samp
    pvalues = []
    for pid in range(snt_mat_b.shape[1]):
        test_result = stats.ks_2samp(snt_mat_a[:,pid],snt_mat_b[:,pid])
        pvalues += [test_result.pvalue]

    # combine pvalues to conclude about singular hypothesis
    #combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    combined_pvalue = stats.combine_pvalues(pvalues, method='tippett')

    return combined_pvalue[1]

print('KS2samp:')
for a in range(5):
    for b in range(5):
        #print(['a', grns[grn_mat[a]], 'b', grns[grn_mat[b]]])
        pvalue = ks2samp_grns(a,b)
        tresult = ttest_grns(a,b)
        if( pvalue < 0.005 and ( a != b ) ):
            print('**\t\t', end='')
        elif( pvalue < 0.05 and ( a != b ) ):
            print('*\t\t', end='')
        else:
            print('[NS]\t', end='')
        print('\t'.join([str(el) for el in [a,b,pvalue]]))

###

# %%

# PCA

from sklearn.decomposition import PCA

pca = PCA(n_components=3)
pca.fit(snt_mat)

print(pca.explained_variance_ratio_)
print(pca.singular_values_)

# norm_snt_mat has better significance FIXME
pca_snt_mat = pca.transform(snt_mat)

def ks2samp_pca_grns(grn_a_id, grn_b_id):

    grn_a_mask = np.array([ True if grn == grn_a_id else False for grn in grn_mat ])
    grn_b_mask = np.array([ True if grn == grn_b_id else False for grn in grn_mat ])

    snt_mat_a = pca_snt_mat[grn_a_mask,:]
    snt_mat_b = pca_snt_mat[grn_b_mask,:]

    from scipy.spatial.distance import cdist

    from scipy import stats
    #stats.ttest_ind(snt_mat_a,snt_mat_b, equal_var = False)
    pvalues = []
    for pid in range(snt_mat_b.shape[1]):
        test_result = stats.ks_2samp(snt_mat_a[:,0],snt_mat_b[:,0])
        pvalues += [test_result.pvalue]

    # combine pvalues to conclude about singular hypothesis
    #combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')

    return combined_pvalue[1]

print('KS2samp:')
for a in range(5):
    print(['Grn ', a, grns[a]])
for a in range(5):
    for b in range(5):
        pvalue = ks2samp_pca_grns(a,b)
        #print(['a', grns[a], 'b', grns[b]])
        if( pvalue < 0.005 and ( a != b ) ):
            print('**\t\t', end='')
        elif( pvalue < 0.05 and ( a != b ) ):
            print('*\t\t', end='')
        else:
            print('[NS]\t', end='')
        print('\t'.join([str(el) for el in [a,b,pvalue]]))

#plt.scatter(grn_mat, pca_snt_mat)

# %%
# Pair plot with PCA

import matplotlib.pyplot as plt
import pandas as pd

# Seaborn visualization library
import seaborn as sns
# Create the default pairplot

full_mat = np.hstack([grn_mat[:,np.newaxis], snt_mat, pca_snt_mat])

def ks2samp_full(grn_a_id, grn_b_id,randomize=1):

    grn_a_mask = np.array([ True if ( grn == grn_a_id ) and ( np.random.rand() < randomize ) else False for grn in grn_mat ])
    grn_b_mask = np.array([ True if ( grn == grn_b_id ) and ( np.random.rand() < randomize ) else False for grn in grn_mat ])

    snt_mat_a = full_mat[grn_a_mask,1:]
    snt_mat_b = full_mat[grn_b_mask,1:]

    from scipy.spatial.distance import cdist

    import random

    from scipy import stats
    #stats.ttest_ind(snt_mat_a,snt_mat_b, equal_var = False)
    pvalues = []
    order = list(range(snt_mat_b.shape[1]))
    random.shuffle(order)
    for pid in order:
        test_result = stats.ks_2samp(snt_mat_a[pid::snt_mat_b.shape[0],pid],snt_mat_b[:,pid])
        pvalues += [test_result.pvalue]

    # combine pvalues to conclude about singular hypothesis
    #combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    return combined_pvalue[1]

    # combined_pvalue = np.min(pvalues)
    # return combined_pvalue



def ks2samp_full_v_all(grn_a_id):

    grn_a_mask = np.array([ True if grn == grn_a_id else False for grn in grn_mat ])
    grn_b_mask = np.array([ True for grn in grn_mat ])

    snt_mat_a = full_mat[grn_a_mask,1:]
    snt_mat_b = full_mat[grn_b_mask,1:]

    from scipy.spatial.distance import cdist

    from scipy import stats
    #stats.ttest_ind(snt_mat_a,snt_mat_b, equal_var = False)
    pvalues = []
    for pid in range(snt_mat_b.shape[1]):
        test_result = stats.ks_2samp(snt_mat_a[:,pid],snt_mat_b[:,pid])
        pvalues += [test_result.pvalue]

    # combine pvalues to conclude about singular hypothesis
    #combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    return combined_pvalue[1]

    # combined_pvalue = np.min(pvalues)
    # return combined_pvalue


num_neurons = full_mat.shape[0] / len(grns)

print('p-values of Kolmogorov-Smirnoff 2-sample test on SNT + PCA features combined with fisher method:')
print(['num samples per test:',num_neurons/( full_mat.shape[1] - 1 )])
for a in range(5):
    for b in range(5):
        if a == b:
            pvalue = ks2samp_full(a,b,randomize=0.5)
        else:
            pvalue = ks2samp_full(a,b)
        if( pvalue < 0.005 ):
            print('**\t\t', end='')
        elif( pvalue < 0.05 ):
            print('*\t\t', end='')
        else:
            print('[NS]\t', end='')
        print('\t'.join([str(el) for el in [a,b,pvalue]]))
    pvalue = ks2samp_full_v_all(a)
    if( pvalue < 0.005 ):
        print('**\t\t', end='')
    elif( pvalue < 0.05 ):
        print('*\t\t', end='')
    else:
        print('[NS]\t', end='')
    print('\t'.join([str(el) for el in [a,'all',pvalue]]))

# print('kl-divergence:')
# for a in range(5):
#     for b in range(5):
#         if a == b:
#             pvalue = kld_full(a,b,randomize=0.5)
#         else:
#             pvalue = kld_full(a,b)
#         if( pvalue < 0.005 ):
#             print('**\t\t', end='')
#         elif( pvalue < 0.05 ):
#             print('*\t\t', end='')
#         else:
#             print('[NS]\t', end='')
#         print('\t'.join([str(el) for el in [a,b,pvalue]]))
#     pvalue = kld_full_v_all(a)
#     if( pvalue < 0.005 and ( a != b ) ):
#         print('**\t\t', end='')
#     elif( pvalue < 0.05 and ( a != b ) ):
#         print('*\t\t', end='')
#     else:
#         print('[NS]\t', end='')
#     print('\t'.join([str(el) for el in [a,'all',pvalue]]))


# plt.figure()
# sns.pairplot(pd.DataFrame(data=full_mat_with_pca,columns=['grn']+snt_keys+['pca' + str(el) for el in range(pca_snt_mat.shape[1])]))
# plt.savefig(output_directory + "/pairplot_withPCA_v01.png")

# %% Pairplot with PCA

plt.figure()
sns.pairplot(pd.DataFrame(data=full_mat,columns=['grn']+snt_keys+['pca' + str(el) for el in range(pca_snt_mat.shape[1])]))
plt.savefig(output_directory + "/pairplot_pca_v01.png")

# %% PCA scree plot

plt.plot(range(1,len(pca.explained_variance_ratio_)+1),np.cumsum(pca.explained_variance_ratio_))
plt.xlabel('number of components')
plt.ylabel('cumulative explained variance')
plt.savefig(output_directory + "/pca_scree.png")

# %% PCA GRN scatter

#pca_snt_mat = pca.transform(norm_snt_mat)

import matplotlib.colors as mcolors

colors = list(mcolors.TABLEAU_COLORS)

for grn_id in range(5):
    grn_mask = np.array([ True if grn == grn_id else False for grn in grn_mat ])
    x = pca_snt_mat[grn_mask,0]
    y = pca_snt_mat[grn_mask,1]
    plt.scatter(x,y,color=colors[grn_id % len(colors)])
plt.savefig(output_directory + '/pca_scatter_grncolor.png')

# %% tSNE

from sklearn.manifold import TSNE

import seaborn as sns

sns.set(rc={'figure.figsize':(11.7,8.27)})
palette = sns.color_palette("bright", 10)

tsne_snt_mat = TSNE(n_components=2,perplexity=5).fit_transform(snt_mat)

full_mat = np.hstack([grn_mat[:,np.newaxis], snt_mat, pca_snt_mat, tsne_snt_mat])

def ks2samp_full(grn_a_id, grn_b_id):

    grn_a_mask = np.array([ True if grn == grn_a_id else False for grn in grn_mat ])
    grn_b_mask = np.array([ True if grn == grn_b_id else False for grn in grn_mat ])

    snt_mat_a = full_mat[grn_a_mask,1:]
    snt_mat_b = full_mat[grn_b_mask,1:]

    from scipy.spatial.distance import cdist

    from scipy import stats
    #stats.ttest_ind(snt_mat_a,snt_mat_b, equal_var = False)
    pvalues = []
    for pid in range(snt_mat_b.shape[1]):
        test_result = stats.ks_2samp(snt_mat_a[:,pid],snt_mat_b[:,pid])
        pvalues += [test_result.pvalue]

    # combine pvalues to conclude about singular hypothesis
    #combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    return combined_pvalue[1]

    # combined_pvalue = np.min(pvalues)
    # return combined_pvalue



for a in range(5):
    for b in range(5):
        pvalue = ks2samp_full(a,b)
        if( pvalue < 0.005 and ( a != b ) ):
            print('**\t\t', end='')
        elif( pvalue < 0.05 and ( a != b ) ):
            print('*\t\t', end='')
        else:
            print('[NS]\t', end='')
        print('\t'.join([str(el) for el in [a,b,pvalue]]))

# plt.figure()
# sns.pairplot(pd.DataFrame(data=full_mat,columns=['grn']+snt_keys+['pca' + str(el) for el in range(pca_snt_mat.shape[1])]+['tSNE' + str(el) for el in range(tsne_snt_mat.shape[1])]))
# plt.savefig(output_directory + "/pairplot_pca_tsne_v01.png")

# %% tSNE scatter
#
# import matplotlib.colors as mcolors
#
# colors = list(mcolors.TABLEAU_COLORS)
#
# for grn_id in range(5):
#     grn_mask = np.array([ True if grn == grn_id else False for grn in grn_mat ])
#     x = tsne_snt_mat[grn_mask,0]
#     y = tsne_snt_mat[grn_mask,1]
#     plt.scatter(x,y,color=colors[grn_id % len(colors)])
# plt.savefig(output_directory + '/tsne_scatter_grncolor.png')
