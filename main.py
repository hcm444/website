import requests
import time
import geopandas as gpd
import sqlite3

conn1 = sqlite3.connect('databases/db1.sqlite3')
c1 = conn1.cursor()
c1.execute('''CREATE TABLE IF NOT EXISTS flights (icao24 text, callsign text, origin_country text, time_position real, 
 last_contact real, longitude real, latitude real, geo_altitude real, on_ground int, velocity real, true_track real, 
 vertical_rate real, sensors real, baro_altitude real, timestamp int)''')
conn1.commit()

conn2 = sqlite3.connect('databases/db2.sqlite3')
c2 = conn2.cursor()
c2.execute('''CREATE TABLE IF NOT EXISTS flights (icao24 text, callsign text, origin_country text, time_position real, 
 last_contact real, longitude real, latitude real, geo_altitude real, on_ground int, velocity real, true_track real, 
 vertical_rate real, sensors real, baro_altitude real, timestamp int)''')
conn2.commit()

def track_flights(username, password, file, database):
    url = "https://opensky-network.org/api/states/all"
    shapefile = gpd.read_file(file)
    shapefile = shapefile.to_crs(epsg=4326)
    shapefile_boundary = shapefile.geometry.unary_union.bounds
    params = {"lamin": shapefile_boundary[1], "lomin": shapefile_boundary[0],
              "lamax": shapefile_boundary[3], "lomax": shapefile_boundary[2]}
    response = requests.get(url, auth=(username, password), params=params)
    data = response.json()["states"]
    timestamp = int(time.time())
    aircraft_df = gpd.GeoDataFrame(
        {"icao24": [item[0] for item in data],
         "callsign": [item[1] for item in data],
         "origin_country": [item[2] for item in data],
         "time_position": [item[3] for item in data],
         "last_contact": [item[4] for item in data],
         "longitude": [item[5] for item in data],
         "latitude": [item[6] for item in data],
         "geo_altitude": [item[7] for item in data],
         "on_ground": [item[8] for item in data],
         "velocity": [item[9] for item in data],
         "true_track": [item[10] for item in data],
         "vertical_rate": [item[11] for item in data],
         "sensors": [item[12] for item in data],
         "baro_altitude": [item[13] for item in data],
         "timestamp": timestamp},
        geometry=gpd.points_from_xy([item[5] for item in data], [item[6] for item in data]),
        crs=shapefile.crs
    )
    aircraft_within = gpd.sjoin(aircraft_df, shapefile, op="within")
    conn = sqlite3.connect(database)
    c = conn.cursor()
    for index, row in aircraft_within.iterrows():
        c.execute('''INSERT INTO flights 
                     (icao24, callsign, origin_country, time_position, 
last_contact, longitude, latitude, geo_altitude, on_ground, velocity, true_track, 
vertical_rate, sensors, baro_altitude, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (row["icao24"],
                   row["callsign"],
                   row["origin_country"],
                   row["time_position"],
                   row["last_contact"],
                   row["longitude"],
                   row["latitude"],
                   row["geo_altitude"],
                   row["on_ground"],
                   row["velocity"],
                   row["true_track"],
                   row["vertical_rate"],
                   row["sensors"],
                   row["baro_altitude"],
                   row["timestamp"]))
    conn.commit()
