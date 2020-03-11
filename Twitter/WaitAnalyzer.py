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
        NeuralShaping(self.db)
        #Analysis(self.db)
        #NeuralNet.test(self.db)



if __name__ == '__main__':
    WaitAnalyzer()
