from datetime import datetime

import sqlite3

class SQLiteDB():

    def __init__(self, db_name = 'waits.db'):
        self.conn = sqlite3.connect(db_name)
        self.curs = self.conn.cursor()

        self.curs.execute('''CREATE TABLE IF NOT EXISTS wait_times (
                            id integer,
                            year integer NOT NULL,
                            month integer NOT NULL,
                            day integer NOT NULL,
                            weekday integer NOT NULL,
                            hour integer NOT NULL,
                            wait_time integer NOT NULL,
                            PRIMARY KEY (year, month, day, hour)
                            )''')

    def insert(self, id, dt, wait_time):
        vals = (id, dt.year, dt.month, dt.day, dt.weekday(), dt.hour, wait_time)
        try:
            self.curs.execute("INSERT INTO wait_times VALUES (?,?,?,?,?,?,?)", vals)
            self.conn.commit()
        except:
            print("Failed to insert {}, must be duplicate".format(vals))

    def get_last_id(self):
        self.curs.execute("SELECT MAX(id) as max_id FROM wait_times")
        return self.curs.fetchone()[0]


if __name__ == '__main__':
    db_instance = SQLiteDB()
