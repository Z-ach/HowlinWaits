from SQLiteDB import SQLiteDB
from TweetFetch import TwitterParser
from Analysis import Analysis
from pathlib import Path

from NeuralShaping import NeuralShaping

from matplotlib import pyplot as plt


class WaitAnalyzer():

    def __init__(self):
        db_path = Path(__file__).resolve().parent.parent
        db_path = db_path.joinpath('Data/waits.db')
        self.db = SQLiteDB(db_path)
        self.parser = TwitterParser(self.db)
        internal_nodes = [pow(2, x) for x in range(9, 11)]
        NeuralShaping(self.db.get_all(), ['hour', 'weekday', 'day'], internal_nodes, range(1, 3))
        #Analysis(self.db)
        #NeuralNet.test(self.db)


if __name__ == '__main__':
    WaitAnalyzer()
