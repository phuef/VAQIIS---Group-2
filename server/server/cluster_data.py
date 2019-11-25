import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn.cluster as cluster
import time
import hdbscan
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import freeze_support
import json
from osgeo import ogr, osr
import math
import os

sns.set_context("poster")
sns.set_color_codes()
plot_kwds = {"alpha": 1, "s": 5, "linewidths": 0}

with open(
    "C:\\Users\\hfock\\Documents\\Uni\\7. Semester\\Studienprojekt\\Daten\\cluster_dataset\\routes\\1\\1406176952000",
    "rt",
) as f:
    data = np.loadtxt(f)


def seperate_into_levels(data: np.array, level_index: int):
    min_val = data.T[level_index].min()
    max_val = data.T[level_index].max()
    div = (max_val - min_val) / 10
    steps = []
    levels = []

    for i in range(0, 10):
        steps.append(i * div)

    for i, step in enumerate(steps):
        levels.append(data[np.where(data.T[level_index] >= step + min_val)])

    return levels


def create_regons_of_interest_from_level(
    seperation: list, lat_long: tuple = (0, 1), buffer: float = 10) -> dict:
    lat, lng = lat_long

    def singel_region(cluster: np.ndarray) -> ogr.Geometry:
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)
        for row in cluster:
            point = ogr.CreateGeometryFromWkt(f"POINT ({row[lng]} {row[lat]})")
            multipoint.AddGeometry(point)

        multipoint = convert_sr(multipoint)
        buffer_geom = multipoint.Buffer(buffer)

        hull = buffer_geom.ConvexHull()
        hull = convert_sr(hull, epsg_source=3044, epsg_target=4326)

        return hull

    multipolygon = {"type": "MultiPolygon", "coordinates": []}
    for cluster in seperation:
        json_roi = json.loads(singel_region(cluster).ExportToJson())
        multipolygon["coordinates"].append(json_roi["coordinates"])

    return multipolygon


def spatial_cluster(level) -> np.ndarray:
    lables = hdbscan.HDBSCAN(min_cluster_size=15).fit_predict(level)
    num_lables = len(set(lables))
    seperation = []
    for i in range(num_lables):
        ids = np.where(lables == i)
        seperation.append(level[ids])

    return seperation


def convert_sr(geom: ogr.Geometry, epsg_source: int = 4326, epsg_target: int = 3044) -> ogr.Geometry:
    source = osr.SpatialReference()
    source.ImportFromEPSG(epsg_source)

    target = osr.SpatialReference()
    target.ImportFromEPSG(epsg_target)

    transform = osr.CoordinateTransformation(source, target)

    geom.Transform(transform)

    return geom


def main():
    levels = seperate_into_levels(data, 3)
    cluster = spatial_cluster(levels[-1])
    mp = create_regons_of_interest_from_level(cluster)
    with open("multiF.json", "wt") as f:
        json.dump(mp, f)


if __name__ == "__main__":
    main()
