import numpy as np
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
import pickle


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
    seperation: list, lat_long: tuple = (0, 1), buffer: float = 5
) -> dict:
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
    for i, cluster in enumerate(seperation):
        try:
            json_roi = json.loads(singel_region(cluster).ExportToJson())
            multipolygon["coordinates"].append(json_roi["coordinates"])
        except KeyError:
            print(f"Error at cluster {i}")
    return multipolygon


def spatial_cluster(level) -> np.ndarray:
    lables = hdbscan.HDBSCAN(min_cluster_size=15).fit_predict(level)
    num_lables = np.unique(lables).max()
    seperation = []
    for i in range(num_lables):
        ids = np.where(lables == i)
        seperation.append(level[ids])

    return seperation


def convert_sr(
    geom: ogr.Geometry, epsg_source: int = 4326, epsg_target: int = 3044
) -> ogr.Geometry:
    source = osr.SpatialReference()
    source.ImportFromEPSG(epsg_source)

    target = osr.SpatialReference()
    target.ImportFromEPSG(epsg_target)

    transform = osr.CoordinateTransformation(source, target)

    geom.Transform(transform)

    return geom


def main(path):
    with open(path, "rt") as f:
        data = np.loadtxt(f)

    t0 = time.perf_counter()

    levels = seperate_into_levels(data, 3)

    #########################################

    t1 = time.perf_counter()
    print(f"Time for leveling: {t1-t0}")

    with ProcessPoolExecutor() as executer:
        level_cluster = executer.map(spatial_cluster, levels)

    t2 = time.perf_counter()
    print(f"Time for clustering: {t2-t1}")

    with ProcessPoolExecutor() as executer:
        rois_per_level = executer.map(create_regons_of_interest_from_level, level_cluster)

    t3 = time.perf_counter()
    print(f"Time for rois: {t3-t2}")
    print(f"Time for completion: {t3-t0}")

    rois_per_level = list(rois_per_level)

    #########################################

    # t1 = time.perf_counter()
    # print(f"Time for leveling: {t1-t0}")

    # level_cluster = []
    # for level in levels:
    #     level_cluster.append(spatial_cluster(level))

    # t2 = time.perf_counter()
    # print(f"Time for clustering: {t2-t1}")

    # rois_per_level = []
    # for cluster in level_cluster:
    #     rois_per_level.append(create_regons_of_interest_from_level(cluster))

    # t3 = time.perf_counter()
    # print(f"Time for rois: {t3-t2}")
    # print(f"Time for completion: {t3-t1}")

    #########################################

    pickle.dump(rois_per_level, open("server\\server\\data_foder\\rois.p", "wb"))
    

if __name__ == "__main__":
    freeze_support()
    main(
        "C:\\Users\\hfock\\Documents\\Uni\\7. Semester\\Studienprojekt\\Daten\\cluster_dataset\\routes\\1\\1406176952000"
    )

