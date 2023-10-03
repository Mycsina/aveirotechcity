import functools
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
                        "hbxyqRw8XaDPbQb9az1RuZowZvgYBf_FO90BYiRz5PciaPbPIPYFgHZSG_KrVmfw7sdVq7p1R0DQT1yHwdGYkA==",
                        "http://localhost:8086")


@app.route("/get_locations")
@functools.cache
def get_locations():
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
                |> range(start: -45d, stop: -30d)
                |> filter(fn: (r) => r["longitude"] == "{pair[0]}")
                |> filter(fn: (r) => r["latitude"] == "{pair[1]}")
            """
        if len(list(session.query(query))) > 0:
            validated_pairs.append({"longitude": pair[0], "latitude": pair[1]})
    return flask.jsonify(validated_pairs)


@app.route("/get_data", methods=["POST"])
def get_graph():
    # fields = request.form["fields"].split(",")
    # t_start = request.form["t_start"]
    # t_end = request.form["t_end"]
    # sensor = request.form["sensor"]
    fields= "carbon_dioxide"
    t_start= "2023-09-03T05:00:00.000Z"
    t_end= "2023-09-15T05:45:00.000Z"
    sensor= "5d1cb61fdf701404a1973c44_monitar"
    query = f"""
    from(bucket: "{session.bucket}")
        |> range(start: {t_start}, stop: {t_end})
        |> filter(fn: (r) => r["device name"] == "{sensor}")
        |> filter(fn: (r) => r["_field"] == "{fields}")
        """
    results = session.query(query)
    # TODO retrieve multiple fields and separate them based on _field, making one plot per field
    times = list(unpack(results, "_time"))
    values = list(unpack(results))
    df = pd.DataFrame({"time": times, "value": values})
    plot = sns.lineplot(data=df, x="time", y="value")
    plot.tick_params(
        axis='x',
        which='both',
        bottom=False,
        top=False,
        labelbottom=False)
    plot.legend()
    tmpname = f"{time.time()}.png"
    plot.figure.savefig("s.png")
    return render_template("image_template.html", image=tmpname)


if __name__ == '__main__':
    # get_graph()
    app.run(port=9092)
