import os

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
from dotenv import load_dotenv

from influxInteraction import InfluxSession

load_dotenv()

session = InfluxSession("sensor", "hack",
                        "eb2kn5YQql-0vgBZkaoMEBGEemvVxRjQ-fv98RX5Og3ikY2p84BEpCgWVf4kn1OY5o1YbEU5cHM7zLJKNiuX1A==",
                        "http://localhost:8086")

FILE_DIR = "hackathon_air_meteo_noise_csv"
METEO = "hackathon_meteo_"
NOISE = "hackathon_noise_"
AIR = "hackathon_air_"

raw_meteodata = []
raw_noisedata = []
raw_airdata = []

for file in os.walk(FILE_DIR):
    if file[0] == FILE_DIR:
        for f in file[2]:
            if f.startswith(METEO):
                raw_meteodata.append(pd.read_csv(os.path.join(FILE_DIR, f), sep=";"))
            elif f.startswith(NOISE):
                raw_noisedata.append(pd.read_csv(os.path.join(FILE_DIR, f), sep=";"))
            elif f.startswith(AIR):
                raw_airdata.append(pd.read_csv(os.path.join(FILE_DIR, f), sep=";"))

col_units_map = {}
for lst in [raw_meteodata, raw_noisedata, raw_airdata]:
    for df in lst:
        # Remove units
        for col in df.columns:
            if " (" in col:
                col_units_map[col.split(" (")[0]] = col.split(" (")[1][:-1]
        df.columns = [col.split(" (")[0] for col in df.columns]
        # Convert types
        df["device name"] = df["device name"].astype("string")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        # Replace NaN with first value
        df["device name"].ffill(inplace=True)
        df["latitude"].ffill(inplace=True)
        df["longitude"].ffill(inplace=True)

for df in raw_airdata:
    df.set_index("timestamp", inplace=True)
    session.write(df, "air", ["device name", "latitude", "longitude"])
for df in raw_noisedata:
    df.set_index("timestamp", inplace=True)
    session.write(df, "noise", ["device name", "latitude", "longitude"])
for df in raw_meteodata:
    df.set_index("timestamp", inplace=True)
    session.write(df, "meteo", ["device name", "latitude", "longitude"])
