from datetime import datetime, timedelta

import pandas as pd

class Analysis():

    def __init__(self, db):
        self.df = db.get_all()
        rn = datetime.now()
        rn = rn + timedelta(days=-31)
        limited = self.df.query('_date > {}'.format(rn.timestamp()))

        df_week = limited.groupby('weekday')
        df_list = [df_week.get_group(day) for day in range(1, 7)]

        for df in df_list:
            print(df)
            print(df['wait_time'].mean())


        times = limited.groupby(['weekday', 'hour'], as_index=False)
        mean_times = times['wait_time'].mean()
        print(mean_times.sort_values(by=['wait_time']).head())

    class EWMAnalysis():
        pass
