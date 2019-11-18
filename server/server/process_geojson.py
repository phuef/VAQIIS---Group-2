import json
from osgeo import ogr
import progressbar

widgets=[
    ' [', progressbar.Timer(), '] ',
    progressbar.Counter(),
    progressbar.Bar(),
    ' (', progressbar.AdaptiveETA(), ') ',
]


insert_list = []
delete_list = []


def split_feature(feature: dict, split_point: tuple, index: int):
    feature1 = json.loads(json.dumps(feature))
    feature2 = json.loads(json.dumps(feature))
    try:
        coords = feature["geometry"]["coordinates"]
        split_index = coords.index(list(split_point))
        coords1 = coords[: split_index + 1]
        coords2 = coords[split_index:]

        feature1["geometry"]["coordinates"] = coords1
        feature2["geometry"]["coordinates"] = coords2

        insert_list.extend([feature1, feature2])
        delete_list.append(index)

    except ValueError:
        # TO DO
        pass


with open(
    "C:\\Users\\hfock\\Documents\\Uni\\7. Semester\\Studienprojekt\\Daten\\Münster_geojson\\test_700_lines.geojson",
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
with progressbar.ProgressBar(max_value=len(geosjon["features"]), widgets=widgets) as bar:
    for i, feature in enumerate(geosjon["features"]):
        if feature["geometry"]["type"] == "LineString" and not feature["properties"][
            "highway"
        ] in ("footway", "service"):
            feature["properties"]["endpoints"] = []
            new_geojson["features"].append(feature)
        
        bar.update(i)

# create nodes

intersection_set = set()
intersection_points = []
print(len(new_geojson["features"]))
with progressbar.ProgressBar(max_value=len(new_geojson["features"]), widgets=widgets) as bar:
    for i, feature1 in enumerate(new_geojson["features"]):
        start1 = tuple(feature1["geometry"]["coordinates"][0])
        end1 = tuple(feature1["geometry"]["coordinates"][-1])
        cur_geom = ogr.CreateGeometryFromJson(json.dumps(feature1["geometry"]))

        # lines_on_points.append([])
        for j, feature2 in enumerate(new_geojson["features"][i+1:]):
            j = j+i+1
            start2 = tuple(feature2["geometry"]["coordinates"][0])
            end2 = tuple(feature2["geometry"]["coordinates"][-1])

            geom = ogr.CreateGeometryFromJson(json.dumps(feature2["geometry"]))
            intersect = cur_geom.Intersection(geom)
            if intersect.GetGeometryName() == "POINT":
                coord = (intersect.GetX(), intersect.GetY())
                if coord not in intersection_set:
                    intersection_points.append(intersect)
                    intersection_set.add(coord)
                    # lines_on_points[i].append(feature2)

                if coord not in (start1, end1):
                    split_feature(feature1, coord, i)
                if coord not in (start2, end2):
                    split_feature(feature2, coord, j)

        wkt = "POINT (%s %s)"
        if start1 not in intersection_set:
            intersection_set.add(start1)
            point = ogr.CreateGeometryFromWkt(wkt % start1)
            intersection_points.append(point)
            # lines_on_points[i].append(point)
        if end1 not in intersection_set:
            intersection_set.add(end1)
            point = ogr.CreateGeometryFromWkt(wkt % end1)
            intersection_points.append(point)
            # lines_on_points[i].append(point)

        bar.update(i)

# do replacements
delete_list = list(set(delete_list))
delete_list.sort(reverse=True)
for i in delete_list:
    new_geojson["features"].pop(i)
new_geojson["features"].extend(insert_list)

with progressbar.ProgressBar(max_value=len(intersection_points), widgets=widgets) as bar:
    for i, point in enumerate(intersection_points):
        node =  json.loads(json.dumps(node_template))
        outgoing = []
        num_features = len(new_geojson["features"])
        for j, feature in enumerate(new_geojson["features"]):
            if point.Intersects(ogr.CreateGeometryFromJson(json.dumps(feature["geometry"]))):
                outgoing.append(j)
                new_geojson["features"][j]["properties"]["endpoints"].append(num_features)

        node["properties"]["id"] = num_features
        node["properties"]["out"] = outgoing
        node["geometry"] = json.loads(point.ExportToJson())
        new_geojson["features"].append(node)

        bar.update(i)


with open("new_geojson.json", "wt") as f:
    json.dump(new_geojson, f)

