from datetime import datetime

import pandas as pd
import sqlite3

import pytz

pst_tz = pytz.timezone('US/Pacific')

class SQLiteDB():

    def __init__(self, db_name = 'waits.db'):
        self.conn = sqlite3.connect(str(db_name))
        self.curs = self.conn.cursor()

        #create table if one does not exist
        #primary key is time since epoch in seconds, forces unique entries
        self.curs.execute('''CREATE TABLE IF NOT EXISTS wait_times (
                            id integer,
                            _date date NOT NULL,
                            year integer NOT NULL,
                            month integer NOT NULL,
                            day integer NOT NULL,
                            weekday integer NOT NULL,
                            hour integer NOT NULL,
                            wait_time integer NOT NULL,
                            PRIMARY KEY (_date)
                            )''')

        self.curs.execute('''CREATE TABLE IF NOT EXISTS weather (
                            _date date NOT NULL,
                            year integer NOT NULL,
                            month integer NOT NULL,
                            day integer NOT NULL,
                            hour integer NOT NULL,
                            feels_like_temp integer NOT NULL,
                            precip_intensity float NOT NULL,
                            precip_probability float NOT NULL,
                            weather_summary string,
                            PRIMARY KEY (year, month, day, hour))''')

    #attempt to insert new data, catch exception if data is not unique
    def insert_wait_time(self, id, dt, wait_time):
        vals = (id, dt.timestamp(), dt.year, dt.month, dt.day, dt.weekday(), dt.hour, wait_time)
        try:
            self.curs.execute("INSERT INTO wait_times VALUES (?,?,?,?,?,?,?,?)", vals)
            self.conn.commit()
        except:
            print("Failed to insert {}, must be duplicate".format(vals))

    #get last saved id for TweetFetch
    def get_last_wait_id(self):
        self.curs.execute("SELECT MAX(id) as max_id FROM wait_times")
        return self.curs.fetchone()[0]

    #sql -> pandas fetch, used for analysis
    def get_wait_times(self):
        return pd.read_sql("SELECT * FROM wait_times", self.conn)

    #insert new weather data, if already exists replace (this is handy when replacing out-of-date forecasts)
    def insert_weather(self, dt, feels_like_temp, precip_intensity, precip_probability, summary = None):
        vals = (dt.timestamp(), dt.year, dt.month, dt.hour, dt.day, feels_like_temp, precip_intensity, precip_probability, summary)
        update_vals = (feels_like_temp, precip_intensity, precip_probability, summary, dt.timestamp())
        self.curs.execute('''INSERT OR IGNORE INTO weather VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', vals)
        self.curs.execute('''UPDATE weather SET feels_like_temp=?, precip_intensity=?, precip_probability=?, weather_summary=? WHERE _date=?''', update_vals)
        self.conn.commit()
 
    #get the last weather entry, if no entries, start at the first wait-time dt
    def get_last_weather_dt(self):
        self.curs.execute("SELECT MAX(_date) FROM weather")
        timestamp = self.curs.fetchone()[0]
        if timestamp is None:
            self.curs.execute("SELECT MIN(_date) FROM wait_times")
            timestamp = self.curs.fetchone()[0]
        if timestamp is not None:
            return datetime.fromtimestamp(timestamp, pst_tz)
        return None

    def get_all(self):
        return pd.read_sql('''SELECT wt.*, w.feels_like_temp, w.precip_intensity, w.precip_probability, w.weather_summary 
            FROM wait_times wt 
            INNER JOIN weather w ON wt.year=w.year AND wt.month=w.month AND wt.day=w.day AND wt.hour=w.hour;''', self.conn)

if __name__ == '__main__':
    db_instance = SQLiteDB()
