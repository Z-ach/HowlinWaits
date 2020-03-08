from SQLiteDB import SQLiteDB
from TweetFetch import TwitterParser
from Analysis import Analysis
from pathlib import Path

from NeuralNet import NeuralNet


class WaitAnalyzer():

    def __init__(self):
        db_path = Path(__file__).resolve().parent.parent
        db_path = db_path.joinpath('Data/waits.db')
        self.db = SQLiteDB(db_path)
        self.parser = TwitterParser(self.db)
        data = self.db.get_all()
        outputs = data[['wait_time']].to_numpy()
        data = data[['hour', 'weekday', 'day', 'month']].to_numpy()

        nets = list()
        for inner_layer in [16, 32, 64, 128]:
            for epoch in [50, 100, 150]:
                start_shape = (4, inner_layer, 20)
                for j in range(5):
                    net = NeuralNet(shape=start_shape)
                    net.set_rounding(0.25)
                    net.set_train_test_val(0.6, 0.2, 0.2)
                    net.train_model(data=data, labels=outputs, epochs=epoch)
                    nets.append((net, start_shape, epoch))
                    start_shape = start_shape[:-1] + (inner_layer, start_shape[-1])

        for net, start_shape, epochs in nets:
            print(epochs, start_shape, net.avg, net.worst)

        #Analysis(self.db)
        #NeuralNet.test(self.db)



if __name__ == '__main__':
    WaitAnalyzer()
