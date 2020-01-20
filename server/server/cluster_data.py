import json
import math
import os
import pickle
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from multiprocessing import freeze_support
from pprint import pprint

import hdbscan
import numpy as np
import pandas as pd
import sklearn.cluster as cluster
from osgeo import ogr, osr

def devide_by_time(data: pd.DataFrame):
    oldestDate = datetime(data["TIMESTAMP"].min())
    newestDate = datetime(data["TIMESTAMP"].max())

    


    

def extract_data(data) -> pd.DataFrame:
    data_path = os.path.join("data_folder", "dataframe.p")
    t1 = pd.read_csv(data)
    bins = [f"LiveBin_{x}dM" for x in range(1,17)]
    tpm10 = t1[[x for x in bins]].dropna().sum(axis=1)
    # print(tpm10)
    tOut = pd.DataFrame({"TIMESTAMP": t1["TIMESTAMP"], "lat": t1["lat"], "lon": t1["lon"], "pm10": tpm10}).dropna()
    
    try:
        tOld = pd.read_pickle(data_path)
        tNew = tOut.append(tOld, ignore_index = True).drop_duplicates().sort_values("TIMESTAMP")
        tNew.to_pickle(data_path)
        print(tNew)
    except:
        tOut.to_pickle(data_path)
        print(tOut)
    
    return tNew

def seperate_into_levels(data: np.ndarray, level_index: int):
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
    seperation: list, lat_long: tuple = (1, 2), buffer: float = 5
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
            roi = json.loads(singel_region(cluster).ExportToJson())
            multipolygon["coordinates"].append(roi["coordinates"])
        except KeyError:
            print(f"Error at cluster {i}")
    return multipolygon


def spatial_cluster(level, lat=1, lon=2) -> np.ndarray:
    coordinates = level.T[[lat, lon]]
    lables = hdbscan.HDBSCAN(min_cluster_size=5).fit_predict(coordinates.T)
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


def main(fileBuffer):
    data = extract_data(fileBuffer)

    time_seperation = devide_by_time(data)

    t0 = time.perf_counter()

    levels = seperate_into_levels(data, 3)

    #########################################

    # t1 = time.perf_counter()
    # print(f"Time for leveling: {t1-t0}")

    # with ProcessPoolExecutor() as executer:
    #     level_cluster = executer.map(spatial_cluster, levels)

    # t2 = time.perf_counter()
    # print(f"Time for clustering: {t2-t1}")

    # with ProcessPoolExecutor() as executer:
    #     rois_per_level = executer.map(create_regons_of_interest_from_level, level_cluster)

    # t3 = time.perf_counter()
    # print(f"Time for rois: {t3-t2}")
    # print(f"Time for completion: {t3-t0}")

    # rois_per_level = list(rois_per_level)
    # out = {}

    #########################################

    t1 = time.perf_counter()
    print(f"Time for leveling: {t1-t0}")

    level_cluster = []
    for level in levels:
        level_cluster.append(spatial_cluster(level))

    t2 = time.perf_counter()
    print(f"Time for clustering: {t2-t1}")

    rois_per_level = []
    for cluster in level_cluster:
        rois_per_level.append(create_regons_of_interest_from_level(cluster))

    t3 = time.perf_counter()
    print(f"Time for rois: {t3-t2}")
    print(f"Time for completion: {t3-t1}")

    #########################################
    # with open("test.json", "wt") as f:
    #     f.write(str(rois_per_level[0]))
    pickle.dump(rois_per_level, open(os.path.join("server", "data_folder", "rois.p"), "wb"))
    

if __name__ == "__main__":
    os.chdir(os.path.join("server", "server"))
    freeze_support()
    path = "C:\\Users\\hfock\\Documents\\Uni\\7. Semester\\Studienprojekt\\VAQIIS---Group-2\\data_extraction\\2019-12-19_fasttable.csv"
    with open(path, "rt") as f:
        main(f)
