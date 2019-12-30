from datetime import datetime, timedelta

import pandas as pd

import matplotlib

class Analysis():

    def __init__(self, db):
        self.df = db.get_all()
        self.rn = datetime.now()
        #self.avg_weekday_hours(12)
        print(self.get_current_avgs())

    def avg_weekday_hours(self, month):
        data = self.df.query('month=={} & year=={}'.format(month, self.rn.year))
        data = data.groupby(['weekday', 'hour'], as_index=False).mean().sort_values(by=['weekday', 'hour'])
        print(data[['weekday', 'hour', 'wait_time']])

    def get_current_avgs(self, using=31, as_dict=True):
        last_days = self.rn + timedelta(days=-using)
        data = self.df.query('_date > {}'.format(last_days.timestamp()))
        data = data.groupby(['weekday', 'hour']).mean().sort_values(by=['weekday', 'hour'])
        if as_dict: return data.groupby(level=0).apply(lambda data: data.xs(data.name)['wait_time'].to_dict()).to_dict()
        return data[['wait_time']]

    class EWMAnalysis():
        pass
