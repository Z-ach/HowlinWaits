import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
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

    def __init__(self, shape):
        self.model = self.create_layers(shape)
        self.distrib = (.8, .1, .1)
        self.rounding = 0.25
        self.avg, self.worst = 0, 0

    def set_train_test_val(self, train, test, val):
        self.distrib = (train, test, val)

    def create_layers(self, net_shape):
        inputs = keras.Input(shape=net_shape[0])
        dense = layers.Dense(net_shape[1], activation='relu')
        x = dense(inputs)
        for lyr in net_shape[2:-1]:
            x = layers.Dense(lyr, activation='relu')(x)
        output = layers.Dense(net_shape[-1])(x)
        return keras.Model(inputs=inputs, outputs=output)

    def set_rounding(self, rounding):
        self.rounding = int(1/rounding)

    def train_model(self, data, labels, epochs):
        partition_count = [int(pct * len(data)) for pct in self.distrib]
        idxs = [0, partition_count[0], partition_count[0] + partition_count[1], -1]

        rounded = np.asarray([round(element[0] * self.rounding) for element in labels.tolist()])

        data_x = [data[idxs[x]:idxs[x + 1]] for x in range(3)]
        data_y = [rounded[idxs[x]:idxs[x + 1]] for x in range(3)]

        self.model.compile(optimizer=keras.optimizers.RMSprop(),
                           # Loss function to minimize
                           loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                           # List of metrics to monitor
                           metrics=['sparse_categorical_accuracy'])

        history = self.model.fit(data_x[0], data_y[0],
                                 batch_size=64,
                                 epochs=epochs,
                                 # We pass some validation for
                                 # monitoring validation loss and metrics
                                 # at the end of each epoch
                                 validation_data=(data_x[2], data_y[2]))

        print('\nhistory dict:', history.history)

        self.avg, self.worst = self.get_stats(data_x[1], data_y[1])

    def get_stats(self, data, actuals):
        predictions = self.model.predict(data)
        deltas = list()
        max_delta = 0
        for prediction, actual in zip(predictions, actuals):
            guess = np.argmax(prediction) * 0.25
            actual *= 0.25
            delta = abs(guess - actual)
            max_delta = max(delta, max_delta)
            deltas.append(delta)
        deltas = np.asarray(deltas)
        return np.average(deltas), np.max(deltas)


def test(df):
    out_size = 20
    inputs = keras.Input(shape=(4,))
    dense = layers.Dense(64, activation='relu')
    x = dense(inputs)

    x = layers.Dense(64, activation='relu')(x)
    outputs = layers.Dense(out_size)(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name='sample_network')

    print(model.summary())

    labels = ['hour', 'weekday', 'day', 'month', 'wait_time']
    data_x = df[labels[:len(labels) - 1]].to_numpy()
    data_y = df[labels[len(labels) - 1]].to_numpy()
    data_len = len(data_x)
    half_data = int(data_len / 2)

    val_size = int(data_len * 0.1)
    #np.random.seed(99)
    #np.random.shuffle(data_x)
    #np.random.seed(99)
    #np.random.shuffle(data_y)

    tmp_onehot = [(val * 4) / 4 for val in data_y]
    onehot_y = np.asarray(tmp_onehot)
    # round data to nearest 1/4, then onehot
    '''for index, entry in enumerate(data_y):
        val = round((entry * 4) / 4)
        onehot_y[index] = onehot(val, classes, 0.25)
    '''

    print(data_len, half_data, val_size)

    train_x, train_y = data_x[:-val_size, :len(labels) - 1], onehot_y[:-val_size]
    val_x, val_y = data_x[-val_size:, :len(labels) - 1], onehot_y[-val_size:]

    print(train_x.shape, train_y.shape)
    print(val_x.shape, val_y.shape)

    model.compile(optimizer=keras.optimizers.RMSprop(),  # Optimizer
                  # Loss function to minimize
                  loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  # List of metrics to monitor
                  metrics=['sparse_categorical_accuracy'])

    print('# Fit model on training data')
    history = model.fit(train_x, train_y,
                        batch_size=64,
                        epochs=100,
                        # We pass some validation for
                        # monitoring validation loss and metrics
                        # at the end of each epoch
                        validation_data=(val_x, val_y))

    print('\nhistory dict:', history.history)

    #results = model.evaluate(test_x, test_y, batch_size=128)
    #print('test loss, test acc:', results)

    get_stats(model, data_x, data_y)
    '''
    predictions = model.predict(test_x[:3])
    for prediction, actual in zip(predictions, test_y[:3]):
        cat = np.argmax(prediction) * 0.25
        actual *= 0.25
        print('prediction: {}, actual: {}'.format(cat, actual))
    print('predictions shape:', predictions.shape)
    '''
