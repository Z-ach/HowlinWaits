import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
import pandas as pd

'''
Model information:

Inputs:
    Weather:
        - Temp
        - Rain
    Time:
        - Hour of day
        - Day of week
        - Day of month
        - Month of year
'''

class NeuralNet():

    def __init__(self, input_labels):
        self.input_labels = input_labels
        self.distrib = (.8, .1, .1)
        self.avg, self.worst = 0, 0
        self.patience = 50

    def __repr__(self):
        #return nodes per layer delimited by '-'
        #input layer different, returns list of tuple (not tuple)
        input_layer = str(self.model.layers[0].output_shape[0][1]) + '-'
        rest = '-'.join([str(l.output_shape[1]) for l in self.model.layers[1:]])
        return input_layer + rest

    def set_train_test_val(self, train, test, val):
        self.distrib = (train, test, val)

    def load_model(self, path):
        self.model = keras.models.load_model(path)

    def create_model(self, net_shape):
        inputs = keras.Input(shape=net_shape[0])
        dense = layers.Dense(net_shape[1], activation='relu')
        x = dense(inputs)
        for lyr in net_shape[2:]:
            x = layers.Dense(lyr, activation='relu')(x)
        output = layers.Dense(1)(x)

        model = keras.Model(inputs=inputs, outputs=output)

        model.compile(optimizer=keras.optimizers.RMSprop(),
                      # Loss function to minimize
                      loss='mse',
                      # List of metrics to monitor
                      metrics=['mae', 'mse'])
        self.model = model

    def preprocess_data(self, data):
	#remove data if count of hour < 25
        counts = data['hour'].value_counts()
        data = data[~data['hour'].isin(counts[counts < 25].index)]

        #shuffle data
        data = data.sample(frac=1).reset_index(drop=True)

        #split into input and output
        outputs = data[['wait_time']].to_numpy()
        inputs = data[self.input_labels].to_numpy()

        #partition data into train, test, val for inputs and outputs
        partition_count = [int(pct * len(inputs)) for pct in self.distrib]
        idxs = [0, partition_count[0], partition_count[0] + partition_count[1], -1]
        data_x = [inputs[idxs[x]:idxs[x + 1]] for x in range(3)]
        data_y = [outputs[idxs[x]:idxs[x + 1]] for x in range(3)]

        return data_x, data_y


    def train_model(self, data, epochs, weights_path):
        data_x, data_y = self.preprocess_data(data)
        weights_file = str(weights_path.joinpath('mdl.hd5'))

        early_stop = EarlyStopping(monitor='val_loss', 
                                   patience = self.patience, 
                                   verbose=0, 
                                   mode='min', 
                                   restore_best_weights=True)

        checkpoint = ModelCheckpoint(weights_file, 
                                     save_best_only=True, 
                                     monitor='val_loss', 
                                     mode='min')

        history = self.model.fit(data_x[0], data_y[0],
                                 batch_size=64,
                                 epochs=epochs,
                                 callbacks=[early_stop, checkpoint],
                                 validation_data=(data_x[1], data_y[1]))

        self.avg, self.worst = self.get_stats(data_x[2], data_y[2])

    def get_prediction(self, data):
        inputs = data[self.input_labels].to_numpy()
        return self.model.predict(inputs)

    def get_stats(self, data, actuals):
        predictions = self.model.predict(data)
        deltas = list()
        for prediction, actual in zip(predictions, actuals):
            delta = abs(prediction - actual)
            deltas.append(delta)
        deltas = np.asarray(deltas)
        return np.average(deltas), np.max(deltas)

