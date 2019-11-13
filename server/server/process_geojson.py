import json
from osgeo import ogr
from pprint import pprint

dummyGeom = ogr.Geometry()


insert_list = []
delete_list = []
def split_feature(feature: dict, split_point: tuple, index:int):
    feature1 = json.loads(json.dumps(feature))
    feature2 = json.loads(json.dumps(feature))
    try:
        coords = feature["geometry"]["coordinates"]
        split_index = coords.index(list(split_point))
        coords1 = coords[:split_index+1]
        coords2 = coords[split_index:]

        feature1["geometry"]["coordinates"] = coords1
        feature2["geometry"]["coordinates"] = coords2

        insert_list.extend([feature1, feature2])
        delete_list.append(index)

    except ValueError:
        pass

with open(
    "C:\\Users\\hfock\\Documents\\Uni\\7. Semester\\Studienprojekt\\Daten\\Münster_geojson\\test.geojson",
    "rt",
) as geosjon:
    geosjon = json.load(geosjon)

new_geojson = {
    "type": "FeatureCollection",
    "generator": "overpass-ide",
    "copyright": "The data included in this document is from www.openstreetmap.org. The data is made available under ODbL.",
    "timestamp": "2019-11-11T14:00:02Z",
    "features": [],
}

node_template = {
    "type": "Feature",
    "properties": {},
    "geometry": {},
}

# filter unnesessary ways
for feature in geosjon["features"]:
    if feature["geometry"]["type"] == "LineString" and not feature["properties"][
        "highway"
    ] in ("footway", "service"):
        new_geojson["features"].append(feature)

# create nodes

intersection_set = set()
intersection_points = []
for i, feature1 in enumerate(new_geojson["features"]):
    start = tuple(feature1["geometry"]["coordinates"][0])
    end = tuple(feature1["geometry"]["coordinates"][-1])
    cur_geom = ogr.CreateGeometryFromJson(json.dumps(feature1["geometry"]))

    for j, feature2 in enumerate(new_geojson["features"]):
        geom = ogr.CreateGeometryFromJson(json.dumps(feature2["geometry"]))
        intersect = cur_geom.Intersection(geom)
        if intersect.GetGeometryName() == "POINT":
            coord = (intersect.GetX(), intersect.GetY())
            if coord not in intersection_set:
                intersection_points.append(intersect)
                intersection_set.add(coord)

            if coord not in (start, end):
                print("hi")
                split_feature(feature1, coord, i)

    wkt = "POINT (%s %s)"
    if start not in intersection_set:
        intersection_set.add(start)
        intersection_points.append(ogr.CreateGeometryFromWkt(wkt % start))
    if end not in intersection_set:
        intersection_set.add(end)
        intersection_points.append(ogr.CreateGeometryFromWkt(wkt % end))

# do replacements
for i in delete_list:
    new_geojson["features"].pop(i)
new_geojson["features"].extend(insert_list)



for point in intersection_points:
    node = node_template.copy()

    

    node["geometry"] = json.loads(point.ExportToJson())
    new_geojson["features"].append(node)


with open("new_geojson.json", "wt") as f:
    json.dump(new_geojson, f)

