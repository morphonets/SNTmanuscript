import os
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from umap import UMAP
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load csv data assumed to be in ./csv
from inspect import currentframe, getframeinfo
from pathlib import Path

filename = getframeinfo(currentframe()).filename
parent = Path(filename).resolve().parent
csv_dir = str(parent.joinpath('csv').absolute())
num_grns = 5

# Read each metric csv file into a dictionary, with GRN id as key
data = {}
for grn in range(num_grns):
    filename = csv_dir + '/grn_' + str(grn) + '.csv'
    pdata = pd.read_csv(filename, sep=',')
    data[filename] = pdata

# Concatenate the dictionary items into a single dataframe
pdata = pd.concat(data.values())


# Extract and prepare morphometry data for analysis

# Extract SNT measurements
snt_keys = [k for k in pdata.keys() if k != 'filenameGRN' and k != 'Description']
# Obtain the set of strings of the 5 GRN types
grns = sorted(list(set(pdata['filenameGRN'])))
num_grns = len(grns)
# Dictionary that maps GRN filenames to an integer GRN uid
grn_dict = dict(zip(grns, range(num_grns)))

# Define numpy matrices
snt_mat = pdata[snt_keys].to_numpy()  # Matrix of SNT measurements
# Vector of GRN ids to associate with the metrics vector for each observed cell
grn_mat = np.array([grn_dict[grn] for grn in pdata['filenameGRN']])

# Remove all entries with nan's
nan_mask = ~np.isnan(snt_mat).any(axis=1)
grn_mat = grn_mat[nan_mask]
snt_mat = snt_mat[nan_mask]


# Create the histplot
def plot_histplot(pdata):
    # Remove the non-metric values from the dataframe
    snt_df = pdata.drop(columns=['Description'])
    # Unpivot the dataframe to long format using GRN type as the identifier variable,
    # leaving all other columns as the measured variables
    snt_long = pd.melt(snt_df, "filenameGRN", var_name="var")
    g = sns.FacetGrid(snt_long, hue="filenameGRN", col="var", col_wrap=5, sharex=False, legend_out=True)
    g.map(plt.hist, "value", alpha=.4)
    g.add_legend()
    plt.savefig(str(parent.absolute()) + '/histplot.png')


plot_histplot(pdata)


# Create the heatmap
def plot_heatmap(pdata):
    snt_df = pdata.drop(columns=['Description'])
    snt_df = snt_df.dropna(axis="columns")
    # Aggregate each GRN type using the mean value of each metric across all observations
    snt_df = snt_df.groupby(["filenameGRN"]).mean()
    # Scale the values of each metric by the min-max value across the GRNs, so that all metrics
    # are in the same range [0, 1]
    snt_df = pd.DataFrame(MinMaxScaler().fit_transform(snt_df), index=snt_df.index, columns=snt_df.columns)
    plt.figure(figsize=(8, 15))
    ax = sns.heatmap(snt_df.T)
    plt.savefig(str(parent.absolute()) + '/heatmap.png', bbox_inches='tight')


plot_heatmap(pdata)


def ks2samp_full(grn_a_id, grn_b_id, mat):
    # Compute the 2-sample Kolmogorov-Smirnov test
    warnings.filterwarnings("ignore")
    # Only compare the observations for the two GRN types of interest
    grn_a_mask = np.array([ True if grn == grn_a_id else False for grn in grn_mat ])
    grn_b_mask = np.array([ True if grn == grn_b_id else False for grn in grn_mat ])
    # Ignore column 0 since it holds the GRN integer ids
    snt_mat_a = mat[grn_a_mask, 1:]
    snt_mat_b = mat[grn_b_mask, 1:]

    pvalues = []
    for pid in range(snt_mat_b.shape[1]):
        test_result = stats.ks_2samp(snt_mat_a[:, pid], snt_mat_b[:, pid])
        pvalues += [test_result.pvalue]

    # Combine pvalues to conclude about singular hypothesis
    combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    return combined_pvalue[1]


def generate_report(mat, method):
    # Conduct the 2-sample K-S test on all GRN types against each other (ignoring same-group comparisons)
    # and print the p-values
    print('p-values of K-S 2-sample test on {} features combined with Fisher:'.format(method))

    for a in range(num_grns):
        print('- - - - - - - - -')
        for b in range(num_grns):
            pvalue = ks2samp_full(a, b, mat)
            if( a == b ):
                print('N/A\t', end='')
            elif( pvalue < 0.0001 ):
                print('***\t', end='')
            elif( pvalue < 0.001 ):
                print('**\t', end='')
            elif( pvalue < 0.05 ):
                print('*\t', end='')
            else:
                print('NS\t', end='')
            print('\t'.join([str(el) for el in [a,b,pvalue]]))

    print(str(len(snt_keys)) + " metrics used")
    
    
def visualize_embedding(mat, title):
    # Plot the first two and three components of the dimension-reduced metrics array

    # 3 components
    fig = plt.figure(figsize=(15, 15))
    ax = Axes3D(fig)
    scatter = ax.scatter(mat[:,0], mat[:,1], mat[:,2],
                          s=50, c=grn_mat, cmap=plt.get_cmap("viridis"))

    # 2 components
    fig, ax = plt.subplots(figsize=(10,10))
    scatter = ax.scatter(mat[:,0], mat[:,1],
                         s=50, c=grn_mat, cmap=plt.get_cmap("viridis"))
    plt.legend(handles=scatter.legend_elements()[0], labels=grns)
    plt.title(title)
    plt.show()


# Standardize features by removing the mean and scaling to unit variance
norm_snt_mat = StandardScaler().fit_transform(snt_mat)

# SNT metrics analysis
# Concatenate the integer GRN type id for each observation with the observed measurements array
# along the horizontal axis.
full_mat_snt = np.hstack([grn_mat[:, np.newaxis], norm_snt_mat])
# Print the values of the 2-sample K-S test
generate_report(full_mat_snt, "SNT")

# t-SNE plot
tsne_snt_mat = TSNE(n_components=3, random_state=13, perplexity=30).fit_transform(norm_snt_mat)
visualize_embedding(tsne_snt_mat, "t-SNE")

# UMAP analysis
umap_snt_mat = UMAP(n_components=3, random_state=13).fit_transform(norm_snt_mat)
full_mat_umap = np.hstack([grn_mat[:, np.newaxis], umap_snt_mat])
generate_report(full_mat_umap, "UMAP")
visualize_embedding(umap_snt_mat, "UMAP")

# PCA analysis
pca = PCA(n_components=3)
pca.fit(norm_snt_mat)
print("Explained variance ratio: ", pca.explained_variance_ratio_)
print("Singular values: ", pca.singular_values_)
pca_snt_mat = pca.transform(norm_snt_mat)
full_mat_pca = np.hstack([grn_mat[:, np.newaxis], pca_snt_mat])
generate_report(full_mat_pca, "PCA")
visualize_embedding(pca_snt_mat, "PCA")
