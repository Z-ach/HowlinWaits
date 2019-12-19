from SQLiteDB import SQLiteDB
from TweetFetch import TwitterParser

class WaitAnalyzer():

    def __init__(self):
        self.db = SQLiteDB()
        self.parser = TwitterParser(self.db)

if __name__ == '__main__':
	WaitAnalyzer()
