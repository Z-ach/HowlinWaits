from SQLiteDB import SQLiteDB
from Neural.NeuralNet import NeuralNet

from pathlib import Path
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import pandas.tseries.holiday
import pytz

PRECIP_PROB_MIN = 0.4


class NeuralShaping():

    def __init__(self, data, input_names, node_sizes, mid_lyr_counts):
        '''Specify model params to try

        data            pandas dataframe with data to use for model
        input_names     list of dataframe headers to use as inputs
                        when training
        node_sizes      list of sizes to try for internal nodes
                        currently can only use same size for all layers
        mid_lyr_counts  how many hidden layers there are
                        all will be of size `node_sizes`
        '''
        if 'day_of_year' in input_names:
            self.add_day_of_year(data)
        if 'precip_prob_thresh' in input_names:
            self.add_precip_prob_thresh(data)
        if 'holiday' in input_names:
            self.add_holidays(data)
        self.input_names = input_names
        self.run_models(data, node_sizes, mid_lyr_counts)

    def add_day_of_year(self, data):
        pst_tz = pytz.timezone('US/Pacific')
        days = []
        for timestamp in data['_date']:
            dt = datetime.fromtimestamp(timestamp)
            utc_dt = pytz.utc.localize(dt)
            pst_dt = pst_tz.normalize(utc_dt.astimezone(pst_tz))
            days.append(pst_dt.timetuple().tm_yday)
        data['day_of_year'] = days

    def add_precip_prob_thresh(self, data):
        precip_prob_threshes = []
        for i, precip_prob in enumerate(data['precip_probability']):
            precip_prop_thresh = precip_prob
            if precip_prob < PRECIP_PROB_MIN:
                precip_prop_thresh = 0
            precip_prob_threshes.append(precip_prop_thresh)
        data['precip_prob_thresh'] = precip_prob_threshes

    def add_holidays(self, data):
        holiday_append = []
        day_range = 3
        cal = pandas.tseries.holiday.USFederalHolidayCalendar()
        end_date = (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d')
        holidays = cal.holidays(start='2018-01-01', end=end_date).to_series()
        for timestamp in data['_date']:
            dt = datetime.fromtimestamp(timestamp)
            dt_range = [(dt + timedelta(days=x)).strftime('%Y-%m-%d') for x in [-day_range, day_range + 1]]
            holiday_append.append(1 if len(holidays.loc[dt_range[0]:dt_range[1]]) > 0 else 0)
        data['holiday'] = holiday_append

    def run_models(self, data, node_sizes, mid_lyr_counts):
        start_shape = ()
        epoch_lim = 250
        for node_size in node_sizes:
            for middle_layers in mid_lyr_counts:
                #model setup
                start_shape = (len(self.input_names),) + (node_size,)*middle_layers
                net = NeuralNet(shape=start_shape, input_labels=self.input_names)
                graphs_path = Path(__file__).parent.parent
                graphs_dir = graphs_path.joinpath( 'AutoGraphs/{}/'.format(str(net))).resolve()
                net.set_train_test_val(0.7, 0.2, 0.1)
                net.train_model(data=data, epochs=epoch_lim, weights_path = graphs_dir)

                #model graph output
                self.plot(data.copy(), net, graphs_dir)
                
    def plot(self, data, net, graphs_dir):
        counts = data['hour'].value_counts()
        data = data[~data['hour'].isin(counts[counts < 25].index)]

        for month in range(6, 13):
            #filter by day of week
            queried = data.loc[data['month'] == month]
            queried = queried.loc[queried['year'] == 2019]
            
            #get mean of expected wait times, grouped by weekday and hour
            val_expect = list(queried.groupby(['day', 'hour']).mean()['wait_time'])

            #create input data for net
            val_data = queried.groupby(['day', 'hour']).mean().reset_index()[self.input_names].to_numpy()
            run_outputs = net.model.predict(val_data)
            
            graphs_dir.mkdir(exist_ok=True, parents=True)
           
            plt.figure(figsize=(20,10))
            plt.plot(val_expect, '--bo', label='actual vals')
            plt.plot(run_outputs, '--ro', label='predicted vals')
            plt.legend()
            plt.savefig(graphs_dir.joinpath('fig_month_{}.png'.format(month)))
            plt.close('all')

        for day in range(1, 7):
            #filter by day of week
            queried = data.loc[data['weekday'] == day]
            
            #get mean of expected wait times, grouped by weekday and hour
            val_expect = list(queried.groupby(['weekday', 'hour']).mean()['wait_time'])

            #create input data for net
            
            val_data = queried.groupby(['weekday', 'hour']).mean().reset_index()[self.input_names].to_numpy()
            run_outputs = net.model.predict(val_data)

            plt.plot(val_data[:,0], val_expect, '--bo', label='actual vals')
            plt.plot(val_data[:,0], run_outputs, '--ro', label='predicted vals')
            plt.legend()
            plt.savefig(graphs_dir.joinpath('fig_day_{}.png'.format(day)))
            plt.close('all')

        with open(graphs_dir.joinpath('results.txt'), 'w') as file_:
            file_.write('{}\t{}\t{}\n'.format(str(net), net.avg, net.worst))

