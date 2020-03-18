from SQLiteDB import SQLiteDB
from Twitter.TweetFetch import TwitterParser
from Twitter.Analysis import Analysis
from Weather.WeatherFetch import WeatherParser
from Neural.NeuralManager import NeuralManager

from pathlib import Path
from datetime import datetime


class WaitAnalyzer():

    def __init__(self):
        db_path = Path(__file__).resolve().parent
        db_path = db_path.joinpath('Data/waits.db')
        self.db = SQLiteDB(db_path)
        self.parser = TwitterParser(self.db)
        self.weather_parser = WeatherParser(self.db)
        self.weather_parser.update_weather()

        inputs = ['hour', 'weekday', 'day', 'day_of_year', 'feels_like_temp', 'precip_prob_thresh', 'holiday']
        mgr = NeuralManager(inputs)
        mgr.load_model_and_predict('AutoGraphs/7-2048-2048-2048-2048-1/mdl.hd5', datetime.now(), self.db.get_weather())

        '''
        internal_nodes = [pow(2, x) for x in range(9, 14)]
        NeuralShaping(self.db.get_all(), ['hour', 'weekday', 'day', 'day_of_year', 'feels_like_temp', 'precip_prob_thresh', 'holiday'], internal_nodes, range(1, 5))
        '''
        #Analysis(self.db)
        #NeuralNet.test(self.db)


if __name__ == '__main__':
    WaitAnalyzer()
