import functools
import os
import shutil
import time

import pandas as pd
import seaborn as sns
import flask
from flask import request, render_template
from flask_cors import CORS

from influxInteraction import InfluxSession, unpack

app = flask.Flask(__name__)
CORS(app)
session = InfluxSession("sensor", "hack",
                        "eb2kn5YQql-0vgBZkaoMEBGEemvVxRjQ-fv98RX5Og3ikY2p84BEpCgWVf4kn1OY5o1YbEU5cHM7zLJKNiuX1A==",
                        "http://localhost:8086")
sns.set_theme()


@app.route("/")
def index():
    # TODO: this is a hack, fix it
    marker_id = request.args.get("marker_id")
    print(marker_id)
    lng = -8.6587
    lat = 40.6350
    if marker_id is not None:
        locats = _get_marker_locations()
        if len(locats) > int(marker_id):
            lng, lat = locats[int(marker_id)]["longitude"], locats[int(marker_id)]["latitude"]
    return render_template("aveiro.html", lng=lng, lat=lat)


@functools.cache
def _get_marker_locations():
    query = f"""
    import "influxdata/influxdb/schema"
    schema.tagValues(bucket: "{session.bucket}", tag: "longitude")
    """
    results = session.query(query)
    longitudes = list(unpack(results))
    query = f"""
    import "influxdata/influxdb/schema"
    schema.tagValues(bucket: "{session.bucket}", tag: "latitude")
    """
    latitude = session.query(query)
    latitudes = list(unpack(latitude))
    # find latitude, longitude pairs
    pairs = []
    for longitude in longitudes:
        for latitude in latitudes:
            pairs.append((longitude, latitude))
    validated_pairs = []
    for pair in pairs:
        query = f"""
            from(bucket: "{session.bucket}")
                |> range(start: -45d, stop: -44d)
                |> filter(fn: (r) => r["longitude"] == "{pair[0]}")
                |> filter(fn: (r) => r["latitude"] == "{pair[1]}")
                |> top(n: 1)
            """
        if len(list(session.query(query))) > 0:
            validated_pairs.append({"longitude": pair[0], "latitude": pair[1]})
    return validated_pairs


@app.route("/get_locations")
def get_locations():
    validated_pairs = _get_marker_locations()
    return flask.jsonify(validated_pairs)


@functools.cache
def _get_data(sensor, fields, t_start, t_end):
    times = []
    values = {}
    for field in fields.split(","):
        query = f"""
        from(bucket: "{session.bucket}")
            |> range(start: {t_start}, stop: {t_end})
            |> filter(fn: (r) => r["device name"] == "{sensor}")
            |> filter(fn: (r) => r["_field"] == "{field}")
            """
        results = session.query(query)
        # TODO retrieve multiple fields and separate them based on _field, making one plot per field
        times = list(unpack(results, "_time"))
        values[field] = unpack(results)
    return pd.DataFrame(values, index=times)


@app.route("/get_data", methods=["POST"])
def get_graph():
    # fields = request.form["fields"].split(",")
    # t_start = request.form["t_start"]
    # t_end = request.form["t_end"]
    # sensor = request.form["sensor"]
    for key in request.form:
        print(key, request.form[key])
    fields = "carbon_dioxide,nitrogen_dioxide,ozone,pm_10"
    t_start = "2023-06-03T05:00:00.000Z"
    t_end = "2023-07-15T05:45:00.000Z"
    sensor = "5d1cb61fdf701404a1973c44_monitar"
    df = _get_data(sensor, fields, t_start, t_end)
    plot = sns.lineplot(data=df, legend="auto")
    plot.tick_params(
        axis='x',
        which='both',
        bottom=False,
        top=False,
        labelbottom=False)
    if not os.path.exists("static"):
        os.mkdir("static")
    tmpname = f"static/{time.time()}.png"
    plot.figure.savefig(f"{tmpname}")
    plot.figure.clear()
    return render_template("image_template.html", image=tmpname)


if __name__ == '__main__':
    # Precache the marker locations
    _get_marker_locations()
    print("Precached marker locations")
    if os.path.exists("static"):
        shutil.rmtree("static")
    app.debug = True
    app.run(port=9092)
