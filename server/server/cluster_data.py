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


def extract_data(data) -> pd.DataFrame:
    data_path = os.path.join("data_folder", "dataframe.p")
    t1 = pd.read_csv(data)
    bins = [f"LiveBin_{x}dM" for x in range(1, 17)]
    tpm10 = t1[[x for x in bins]].dropna().sum(axis=1)
    # print(tpm10)
    tOut = pd.DataFrame(
        {
            "TIMESTAMP": t1["TIMESTAMP"],
            "lat": t1["lat"],
            "lon": t1["lon"],
            "pm10": tpm10,
        }
    ).dropna()

    try:
        tOld = pd.read_pickle(data_path)
        tNew = (
            tOut.append(tOld, ignore_index=True)
            .drop_duplicates()
            .sort_values("TIMESTAMP")
        )
        tNew.to_pickle(data_path)
        # print(tNew)
    except:
        tOut.sort_values("TIMESTAMP").to_pickle(data_path)
        # print(tOut)
        tNew = tOut

    return tNew


def devide_by_time(data: pd.DataFrame):
    data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"])
    allDays = data["TIMESTAMP"].dt.normalize().unique()
    numDays = len(allDays)
    seperation = []
    for day in allDays:
        rows_to_day = data[data.TIMESTAMP >= day]
        seperation.append(rows_to_day)

    return seperation


def seperate_into_levels(data: pd.DataFrame) -> list:
    # min_val = data.T[level_index].min()
    min_val = data["pm10"].min()
    # max_val = data.T[level_index].max()
    max_val = data["pm10"].max()
    div = (max_val - min_val) / 10
    steps = []
    levels = []

    for i in range(0, 10):
        steps.append(i * div)

    for i, step in enumerate(steps):
        # levels.append(data[np.where(data.T[level_index] >= step + min_val)])
        level = data[data.pm10 >= step + min_val].reset_index(drop=True)
        levels.append(level)

    return levels


def create_regons_of_interest_from_level(
    seperation: list, buffer: float = 5
) -> dict:

    def singel_region(cluster: pd.DataFrame) -> ogr.Geometry:
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)
        for _, row in cluster.iterrows():
            point = ogr.CreateGeometryFromWkt(f"POINT ({row['lon']} {row['lat']})")
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


def spatial_cluster(level: pd.DataFrame) -> list:
    # coordinates = level.T[[lat, lon]]
    # print(level)
    coordinates = level[["lat", "lon"]].to_numpy()
    lables = hdbscan.HDBSCAN(min_cluster_size=2).fit_predict(coordinates)
    num_lables = np.unique(lables).max()
    seperation = []
    for i in range(num_lables):
        ids = np.where(lables == i)
        seperation.append(level.loc[ids])

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

    t0 = time.perf_counter()

    time_seperation = devide_by_time(data)

    levels = []
    for daySep in time_seperation:
        levels.append(seperate_into_levels(daySep))

    # print(levels)

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

    day_cluster = []
    for day in levels:
        level_cluster = []
        for level in day:
            level_cluster.append(spatial_cluster(level))
        day_cluster.append(level_cluster)

    t2 = time.perf_counter()
    print(f"Time for clustering: {t2-t1}")

    rois_per_day = []
    for day in day_cluster:
        rois_per_level = []
        for cluster in day:
            rois_per_level.append(create_regons_of_interest_from_level(cluster))
        rois_per_day.append(rois_per_level)

    t3 = time.perf_counter()
    print(f"Time for rois: {t3-t2}")
    print(f"Time for completion: {t3-t1}")

    #########################################
    with open("test.json", "wt") as f:
        f.write(str(rois_per_day))

    # pprint(rois_per_day)
    # pickle.dump(
    #     rois_per_day, open(os.path.join("server","data_folder", "rois.p"), "wb")
    # )



if __name__ == "__main__":
    os.chdir(os.path.join("server", "server"))
    freeze_support()
    path = "C:\\Users\\hfock\\Documents\\Uni\\7. Semester\\Studienprojekt\\VAQIIS---Group-2\\data_extraction\\extracted_Data_TOA5_fasttable1_2019_10_29_1029.csv"
    with open(path, "rt") as f:
        main(f)
