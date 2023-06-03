import time
import sched
from map import map_data
from main import track_flights

username = "OPENSKYUSERNAME1"
password = "OPENSKYPASSWORD1"
username2 = "OPENSKYUSERNAME1"
password2 = "OPENSKYPASSWORD2"
path = "static/gadm41_BLR_shp/gadm41_BLR_1.shp"
path2 = "static/gadm41_UKR_shp/gadm41_UKR_1.shp"

scheduler = sched.scheduler(time.time, time.sleep)


def track_BLR():
    track_flights(username, password, path,"databases/db1.sqlite3")
    map_data(path,"BLR","databases/db1.sqlite3")
    scheduler.enter(120, 1, track_BLR)

def track_UKR():
    track_flights(username2, password2, path2,"databases/db2.sqlite3")
    map_data(path2,"UKR","databases/db2.sqlite3")
    scheduler.enter(120, 1, track_UKR)

def track_CROW():
    map_data(path2,"CROW","databases/db.sqlite3")
    scheduler.enter(120, 1, track_CROW)


scheduler.enter(0, 1, track_BLR)
scheduler.enter(0, 1, track_UKR)
scheduler.enter(0, 1, track_CROW)
scheduler.run()
