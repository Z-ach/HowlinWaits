from SQLiteDB import SQLiteDB
from Twitter.TweetFetch import TwitterParser
from Twitter.Analysis import Analysis
from pathlib import Path

from Twitter.NeuralShaping import NeuralShaping

from matplotlib import pyplot as plt


class WaitAnalyzer():

    def __init__(self):
        db_path = Path(__file__).resolve().parent
        db_path = db_path.joinpath('Data/waits.db')
        self.db = SQLiteDB(db_path)
        self.parser = TwitterParser(self.db)
        internal_nodes = [pow(2, x) for x in range(9, 15)]
        NeuralShaping(self.db.get_wait_times(), ['hour', 'weekday', 'day', 'day_of_year'], internal_nodes, range(1, 6))
        #Analysis(self.db)
        #NeuralNet.test(self.db)


if __name__ == '__main__':
    WaitAnalyzer()
