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

data = {}

for csv in os.listdir(csv_dir):
    filename = os.path.join(csv_dir, csv)
    pdata = pd.read_csv(filename, sep=',')
    data[filename] = pdata

pdata = pd.concat(data.values())

# Extract and prepare morphometry data for analysis

# Extract SNT measurements, forgoing certain metrics that resulted in NaN for one cell
snt_keys = [
    k for k in pdata.keys() if k != "projectionGroup"
                               and k != "Description"
                               and k != "Sholl: Max (fitted)"
                               and k != "Sholl: Max (fitted) radius"
                               and k != "Sholl: Degree of Polynomial fit"
]
groups = sorted(list(set(pdata['projectionGroup'])))
num_groups = len(groups)
# Dictionary that maps grn filenames to an integer group uid
group_dict = dict(zip(groups, range(num_groups)))
group_dict_inv = {v: k for k, v in group_dict.items()}
# Define numpy matrices
snt_mat = pdata[snt_keys].to_numpy()  # Matrix of SNT measurements
group_mat = np.array([group_dict[group] for group in pdata['projectionGroup']])
# Remove all entries with nan's
nan_mask = ~np.isnan(snt_mat).any(axis=1)
group_mat = group_mat[nan_mask]
group_labels = [group_dict_inv[group] for group in group_mat]
snt_mat = snt_mat[nan_mask]  # remove from snt_mat last


# Create the histplot
def plot_histplot(pdata):
    snt_df = pdata.drop(columns=['Description'])
    snt_long = pd.melt(snt_df, "projectionGroup", var_name="var")
    g = sns.FacetGrid(snt_long, hue="projectionGroup", col="var", col_wrap=5, sharex=False, legend_out=True)
    g.map(plt.hist, "value", alpha=.4)
    g.add_legend()
    plt.savefig(str(parent.absolute()) + '/histplot.png')


plot_histplot(pdata)


# Create the heatmap
def plot_heatmap(pdata):
    snt_df = pdata.drop(columns=["Description"])
    snt_df = snt_df.dropna(axis="columns")
    snt_df = snt_df.groupby(["projectionGroup"]).mean()
    snt_df = pd.DataFrame(MinMaxScaler().fit_transform(snt_df), index=snt_df.index, columns=snt_df.columns)
    plt.figure(figsize=(8, 15))
    ax = sns.heatmap(snt_df.T)
    plt.savefig(str(parent.absolute()) + '/heatmap.png', bbox_inches='tight')


plot_heatmap(pdata)


def ks2samp_full(group_a_id, group_b_id, mat):
    warnings.filterwarnings("ignore")

    group_a_mask = np.array([True if group == group_a_id else False for group in group_mat])
    group_b_mask = np.array([True if group == group_b_id else False for group in group_mat])

    snt_mat_a = mat[group_a_mask, 1:]
    snt_mat_b = mat[group_b_mask, 1:]

    pvalues = []
    for pid in range(snt_mat_b.shape[1]):
        test_result = stats.ks_2samp(snt_mat_a[:, pid], snt_mat_b[:, pid])
        pvalues += [test_result.pvalue]

    # combine pvalues to conclude about singular hypothesis
    combined_pvalue = stats.combine_pvalues(pvalues, method='fisher')
    return combined_pvalue[1]


def generate_report(mat, method):
    print('p-values of K-S 2-sample test on {} features combined with Fisher:'.format(method))

    for a in range(num_groups):
        print('- - - - - - - - -')
        for b in range(num_groups):
            pvalue = ks2samp_full(a, b, mat)
            if (a == b):
                print('N/A\t', end='')
            elif (pvalue < 0.0001):
                print('***\t', end='')
            elif (pvalue < 0.001):
                print('**\t', end='')
            elif (pvalue < 0.05):
                print('*\t', end='')
            else:
                print('NS\t', end='')
            print('\t'.join([str(el) for el in [a, b, pvalue]]))

    print(str(len(snt_keys)) + " metrics used")


def visualize_embedding(mat, title):
    # 3 components
    # fig = plt.figure(figsize=(15, 15))
    # ax = Axes3D(fig)
    # scatter = ax.scatter(mat[:, 0], mat[:, 1], mat[:, 2],
    #                      s=50, c=group_mat, cmap=plt.get_cmap("viridis"))

    # 2 components
    fig, ax = plt.subplots(figsize=(10, 10))
    scatter = ax.scatter(
        mat[:, 0], mat[:, 1],
        s=50, c=group_mat, cmap=plt.get_cmap("viridis")
    )
    plt.legend(
        handles=scatter.legend_elements()[0],
        labels=[os.path.basename(os.path.normpath(group)) for group in groups]
    )
    plt.title(title)
    plt.show()


def plot_dendrogram(model, group_labels):
    # Create linkage matrix and then plot the dendrogram
    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack([model.children_, model.distances_,
                                      counts]).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, orientation='right', labels=group_labels)


def hcluster(mat, group_labels, feature_label):
    # setting distance_threshold=0 ensures we compute the full tree.
    model = AgglomerativeClustering(distance_threshold=0, n_clusters=None)
    model = model.fit(mat)
    fig, ax = plt.subplots(figsize=(10, 13))
    plt.title('{}: Hierarchical Clustering Dendrogram'.format(feature_label))
    # plot the top three levels of the dendrogram
    plot_dendrogram(model, group_labels)
    plt.show()


norm_snt_mat = StandardScaler().fit_transform(snt_mat)

# SNT metrics analysis
full_mat_snt = np.hstack([group_mat[:, np.newaxis], norm_snt_mat])
generate_report(full_mat_snt, "SNT")
hcluster(norm_snt_mat, group_labels, "SNT metrics")

# t-SNE plot
tsne_snt_mat = TSNE(n_components=2, random_state=13).fit_transform(norm_snt_mat)
visualize_embedding(tsne_snt_mat, "t-SNE")

# UMAP analysis
umap_snt_mat = UMAP(n_components=20, random_state=13).fit_transform(norm_snt_mat)
full_mat_umap = np.hstack([group_mat[:, np.newaxis], umap_snt_mat])
generate_report(full_mat_umap, "UMAP")
visualize_embedding(umap_snt_mat, "UMAP")
hcluster(umap_snt_mat, group_labels, "UMAP")

# PCA analysis
pca = PCA(n_components=3)
pca.fit(norm_snt_mat)
print("Explained variance ratio: ", pca.explained_variance_ratio_)
print("Singular values: ", pca.singular_values_)
pca_snt_mat = pca.transform(norm_snt_mat)
full_mat_pca = np.hstack([group_mat[:, np.newaxis], pca_snt_mat])
generate_report(full_mat_pca, "PCA")
visualize_embedding(pca_snt_mat, "PCA")
hcluster(pca_snt_mat, group_labels, "PCA")
