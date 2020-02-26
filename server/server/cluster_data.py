import json
import math
import os
import pickle
import time
from datetime import datetime

import hdbscan
import numpy as np
import pandas as pd
import sklearn.cluster as cluster
from osgeo import ogr, osr

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp
# from pprint import pprint



def extract_data(data) -> pd.DataFrame:
    """extracts the data from csv file and creates a Dataframe
    
    Arguments:
        data {fileBuffer} -- buffered csv file
    
    Returns:
        pd.DataFrame -- updated dataframe with all available data
    """
    data_path = os.path.join("server", "data_folder", "dataframe.p")
    t1 = pd.read_csv(data)
    # get all pm data, drop all columns without data and sum them up to pm10 data
    bins = ["LiveBin_{}dM".format(x) for x in range(1, 17)]
    tpm10 = t1[[x for x in bins]].dropna().sum(axis=1)
    tOut = pd.DataFrame(
        {
            "TIMESTAMP": t1["TIMESTAMP"],
            "lat": t1["lat"],
            "lon": t1["lon"],
            "pm10": tpm10,
        }
    ).dropna()

    # extend or create dataframe
    try:
        tOld = pd.read_pickle(data_path)
        tNew = (
            tOut.append(tOld, ignore_index=True)
            .drop_duplicates()
            .sort_values("TIMESTAMP")
        )
        tNew.to_pickle(data_path)
    except:
        tOut.sort_values("TIMESTAMP").to_pickle(data_path)
        tNew = tOut

    return tNew


def divide_by_time(data: pd.DataFrame) -> dict:
    """seperates the data by days
    
    Arguments:
        data {pd.DataFrame} -- Dataframe with timestamps
    
    Returns:
        dict -- dictionary with key=Timestamp of the day, value: the data corrosponding to the day
    """
    # convert Timestamps to datetime object
    data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"])
    # get all unique days
    allDays = data["TIMESTAMP"].dt.normalize().unique()
    numDays = len(allDays)
    seperation = {}
    # seperate the data
    for day in allDays:
        rows_to_day = data[data.TIMESTAMP >= day]
        seperation[day] = rows_to_day

    return seperation


def seperate_into_levels(data: pd.DataFrame) -> list:
    """seperates the data into pm10 levels, where each level contains all the 
    data which is higher than the level limit
    
    Arguments:
        data {pd.DataFrame} -- dataframe to be divided
    
    Returns:
        list -- list with 10 lists containing the data
    """
    steps = []
    levels = []

    # create limits
    for i in range(0, 10):
        steps.append(i*10)

    # seperate the data
    for i, step in enumerate(steps):
        level = data[data.pm10 >= step].reset_index(drop=True)
        levels.append(level) 

    return levels


def create_regions_of_interest_from_level(
    seperation: list, buffer: float = 10
) -> dict:
    """creates the Polygons for each level
    
    Arguments:
        seperation {list} -- the level seperated data
    
    Keyword Arguments:
        buffer {float} -- bufferregion around each point (default: {10})
    
    Returns:
        dict/GeoJson -- GeoJson Multipolygon
    """

    def singel_region(cluster: pd.DataFrame) -> ogr.Geometry:
        """creates a polygon surrounding a cluster
        
        Arguments:
            cluster {pd.DataFrame} -- single cluster from a level
        
        Returns:
            ogr.Geometry -- Polygon geometry
        """
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)
        # add each point to the multipoint geometry
        for _, row in cluster.iterrows():
            point = ogr.CreateGeometryFromWkt("POINT ({} {})".format(row['lon'], row['lat']))
            multipoint.AddGeometry(point)

        #create buffer around multipoint
        multipoint = convert_sr(multipoint)
        buffer_geom = multipoint.Buffer(buffer)
        hull = buffer_geom.ConvexHull()
        hull = convert_sr(hull, epsg_source=3044, epsg_target=4326)

        return hull

    # commented lines for merged clusters. Increases computational time
    # merged_regions = ogr.Geometry(ogr.wkbMultiPolygon)
    multipolygon = {"type": "MultiPolygon", "coordinates": []}
    # add polygon to the multipolygon object
    for i, cluster in enumerate(seperation):
        try:
            # single_region_data = singel_region(cluster)
            # merged_regions = merged_regions.Union(single_region_data)
            roi = json.loads(singel_region(cluster).ExportToJson())
            multipolygon["coordinates"].append(roi["coordinates"])


        except KeyError:
            print("Error at cluster {}".format(i))

    # multipolygon = json.loads(merged_regions.ExportToJson())
    return multipolygon


def spatial_cluster(level: pd.DataFrame) -> list:
    """cluster the data for their spatial position
    
    Arguments:
        level {pd.DataFrame} -- level of pm10 data
    
    Returns:
        list -- list of spatial clusters
    """
    coordinates = level[["lat", "lon"]].to_numpy()
    # cluster data
    lables = hdbscan.HDBSCAN(min_cluster_size=2).fit_predict(coordinates)
    # use Hirachical clustering to set a distance threshold. computational time increases a lot 
    # because of larger clusters when dealing with many datapoints
        # lables = cluster.AgglomerativeClustering(n_clusters=None ,distance_threshold=50/10000).fit_predict(coordinates)
    num_lables = np.unique(lables).max()
    seperation = []
    for i in range(num_lables):
        ids = np.where(lables == i)
        seperation.append(level.loc[ids])

    return seperation


def convert_sr(
    geom: ogr.Geometry, epsg_source: int = 4326, epsg_target: int = 3044
) -> ogr.Geometry:
    """converts reference systems of ogr Geometries
    
    Arguments:
        geom {ogr.Geometry} -- geometry where the RS should be changed
    
    Keyword Arguments:
        epsg_source {int} -- epsg code of current reference system (default: {4326})
        epsg_target {int} -- epsg code of target reference system (default: {3044})
    
    Returns:
        ogr.Geometry -- Geometry with transformed reference system
    """
    source = osr.SpatialReference()
    source.ImportFromEPSG(epsg_source)

    target = osr.SpatialReference()
    target.ImportFromEPSG(epsg_target)

    transform = osr.CoordinateTransformation(source, target)

    geom.Transform(transform)

    return geom


def _rois(day):
    """help Method for parallel processing: creates the regions of interrest for each cluster within a day
    
    Arguments:
        day {list} -- all levels of a day
    
    Returns:
        list -- list with rois of each level
    """
    rois_per_level = []
    for cluster in day:
        rois_per_level.append(create_regions_of_interest_from_level(cluster))
    return rois_per_level


def main(fileBuffer):
    """main method
    
    Arguments:
        fileBuffer {fileBuffer} -- buffered csv file
    """
    # extract the data
    data = extract_data(fileBuffer)

    t0 = time.perf_counter()

    # divide data by time
    time_seperation = divide_by_time(data)

    # divide into levels
    levels_per_day = {}
    for day in time_seperation.keys():
        date = str(datetime.utcfromtimestamp(day.astype('O')/1e9).date())
        levels_per_day[date] = seperate_into_levels(time_seperation.get(day))

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
    print("Time for leveling: {}".format(t1-t0))

    # create spatial cluster for each level per day
    day_cluster = {}
    for day in levels_per_day.keys():
        level_cluster = []
        for level in levels_per_day.get(day):
            if not level.empty:
                level_cluster.append(spatial_cluster(level))
            else:
                level_cluster.append([])   
        day_cluster[day] = level_cluster

    t2 = time.perf_counter()
    print("Time for clustering: {}".format(t2-t1))
    
    # parallel execution of roi creation
    # numProcesses = len(day_cluster.keys())
    # with ThreadPoolExecutor(max_workers=numProcesses) as executer:
    #     rois_per_day_list = executer.map(_rois, day_cluster.values())
    # rois_per_day_list = list(rois_per_day_list)

    # sequential execution of roi creation
    for day in day_cluster.keys():
        rois_per_day_list = [_rois(x) for x in day_cluster.values()]

    rois_per_day = {k:v for k,v in zip(day_cluster.keys(), rois_per_day_list)}

    t3 = time.perf_counter()
    print("Time for rois: {}".format(t3-t2))
    print("Time for completion: {}".format(t3-t1))

    #########################################
    # with open("test.json", "wt") as f:
    #     f.write(str(rois_per_day))

    # pprint(rois_per_day)
    
    # save data
    pickle.dump(
        rois_per_day, open(os.path.join("server","data_folder", "rois.p"), "wb")
    )



if __name__ == "__main__":
    os.chdir(os.path.join("server"))
    # freeze_support()
    path = "C:\\Users\\hfock\\Documents\\Uni\\7. Semester\\Studienprojekt\\VAQIIS---Group-2\\data_extraction\\2019-12-19_fasttable.csv"
    with open(path, "rt") as f:
        main(f)
