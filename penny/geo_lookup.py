import os
import csv
import sqlite3


def get_connection():
    db_file = os.path.dirname(os.path.realpath(__file__)) + "/data/locs.db"
    conn = sqlite3.connect(db_file)
    conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')

    return conn


def populate_db(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cities")    

    cur.execute("CREATE TABLE cities(geoname_id INTEGER, continent_code TEXT, continent TEXT, country_iso_code TEXT, country TEXT, region_iso_code TEXT, region TEXT, city TEXT, metro_code TEXT, time_zone TEXT)")
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    with open(cur_dir+"/data/GeoLite2-City-Locations.csv", "rb") as info:
        reader = csv.reader(info)
        for row in reader:
            cur.execute("INSERT INTO cities VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", row)

        conn.commit()


def db_has_data(conn):
    cur = conn.cursor()

    cur.execute("SELECT Count(*) FROM sqlite_master WHERE name='cities';")
    data = cur.fetchone()[0]

    if data > 0:
        cur.execute("SELECT Count(*) FROM cities")
        data = cur.fetchone()[0]
        return data > 0

    return False


def get_places_by_type(place_name, place_type):
    place_name = str(place_name).strip().lower().title()

    conn = get_connection()
    if not db_has_data(conn):
        populate_db(conn)

    cur = conn.cursor()
    cur.execute('SELECT * FROM cities WHERE ' + place_type + ' = "' + place_name + '"')
    rows = cur.fetchall()

    if len(rows) > 0:
        return rows

    if len(place_name) < 4: #maybe it's an iso code
        cur.execute('SELECT * FROM cities WHERE ' + place_type + ' = "' + place_name.upper() + '"')
        rows = cur.fetchall()

    if len(rows) > 0:
        return rows

    cur.close()
    del cur
    conn.close()

    return []
