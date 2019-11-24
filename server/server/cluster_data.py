import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn.cluster as cluster
import time
import hdbscan
from pprint import pprint
from detect_peaks import detect_peaks

sns.set_context("poster")
sns.set_color_codes()
plot_kwds = {"alpha": 1, "s": 5, "linewidths": 0}

with open(
    "C:\\Users\\hfock\\Documents\\Uni\\7. Semester\\Studienprojekt\\Daten\\cluster_dataset\\routes\\1\\1406176952000",
    "rt",
) as f:
    data = np.loadtxt(f)

# data.T[0] = data.T[0]/data.T[0].mean()
# data.T[1] = data.T[1]/data.T[1].mean()

# plt.scatter(data.T[0], data.T[1], **plot_kwds)
# frame = plt.gca()
# frame.axes.get_xaxis().set_visible(False)
# frame.axes.get_yaxis().set_visible(False)
# plt.show()


def plot_clusters(data, algorithm, args, kwds):
    start_time = time.time()
    labels = algorithm(*args, **kwds).fit_predict(data)
    print(labels)
    end_time = time.time()
    palette = sns.color_palette("deep", np.unique(labels).max() + 1)
    colors = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in labels]
    plt.scatter(data.T[1], data.T[0], c=colors, **plot_kwds)
    frame = plt.gca()
    frame.axes.get_xaxis().set_visible(False)
    frame.axes.get_yaxis().set_visible(False)
    plt.title("Clusters found by {}".format(str(algorithm.__name__)), fontsize=24)
    plt.text(
        -0.5, 0.7, "Clustering took {:.2f} s".format(end_time - start_time), fontsize=14
    )
    plt.show()


# plot_clusters(data, cluster.KMeans, (), {'n_clusters':6})


def seperate_into_levels(data: np.array, index):
    min_val = data.T[index].min()
    max_val = data.T[index].max()
    div = (max_val - min_val) / 10
    steps = []
    levels = []

    for i in range(0, 10):
        steps.append(i * div)

    for i, step in enumerate(steps):
        levels.append(data[np.where(data.T[index] >= step + min_val)])

    def get_num_peaks(data, index):
        indexes = detect_peaks(data.T[index], mpd=50)
        print(indexes)
        print(len(indexes))
        return indexes

    # peaks = get_num_peaks(levels[-3], index)


    # plt.plot(levels[-3].T[0], levels[-3].T[1], "--rD", markersize=3, linewidth=.5, markevery=list(peaks))
    # frame = plt.gca()
    # frame.axes.get_xaxis().set_visible(False)
    # frame.axes.get_yaxis().set_visible(False)
    # plt.show()

    plot_clusters(levels[-6], hdbscan.HDBSCAN, (), {'min_cluster_size':15})




seperate_into_levels(data, 3)

