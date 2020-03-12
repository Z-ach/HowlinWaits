from datetime import datetime

import pandas as pd
import sqlite3


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

    #attempt to insert new data, catch exception if data is not unique
    def insert(self, id, dt, wait_time):
        vals = (id, dt.timestamp(), dt.year, dt.month, dt.day, dt.weekday(), dt.hour, wait_time)
        try:
            self.curs.execute("INSERT INTO wait_times VALUES (?,?,?,?,?,?,?,?)", vals)
            self.conn.commit()
        except:
            print("Failed to insert {}, must be duplicate".format(vals))

    #get last saved id for TweetFetch
    def get_last_id(self):
        self.curs.execute("SELECT MAX(id) as max_id FROM wait_times")
        return self.curs.fetchone()[0]

    #sql -> pandas fetch, used for analysis
    def get_all(self):
        return pd.read_sql("SELECT * FROM wait_times", self.conn)


if __name__ == '__main__':
    db_instance = SQLiteDB()
