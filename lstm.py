import numpy as np
import tensorflow as tf
from keras.layers import LSTM as LSTM_Layer
from keras.layers import Dense, Dropout
from keras.models import Sequential

from base_model import BaseModel

physical_devices = tf.config.list_physical_devices("GPU")
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)


class LSTM(BaseModel):
    window = 60

    def train(self) -> None:
        train_values = self.train_data.values.reshape(-1, 1)

        X_train = np.array(
            [train_values[i - self.window:i, 0] for i in range(self.window, len(train_values))]
        )
        y_train = np.array([train_values[i, 0] for i in range(self.window, len(train_values))])

        X_train = np.reshape(X_train, (*X_train.shape, 1))

        neurons = 60
        dropout = 0.2
        loss = "mean_squared_error"
        batch_size = 32
        epochs = 200

        self.model = model = Sequential()
        model.add(LSTM_Layer(neurons, return_sequences=True, input_shape=(X_train.shape[1], 1)))
        model.add(Dropout(dropout))
        model.add(LSTM_Layer(neurons, return_sequences=True))
        model.add(Dropout(dropout))
        model.add(LSTM_Layer(neurons, return_sequences=True))
        model.add(Dropout(dropout))
        model.add(LSTM_Layer(neurons, return_sequences=False))
        model.add(Dropout(dropout))
        model.add(Dense(1))

        model.compile(optimizer="adam", loss=loss)

        model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs)

    def make_predictions(self, n_days: int) -> np.array:
        predictions = []
        X_train_values = self.train_data[-self.window:].values

        for _ in range(n_days):
            X_train = np.array(X_train_values).reshape(1, -1, 1)
            predicted_stock_price = self.model.predict(X_train)[0]
            predictions.append(predicted_stock_price[0])
            X_train_values = np.delete(X_train_values, 0)
            X_train_values = np.concatenate((X_train_values, predicted_stock_price))

        return np.array(predictions)
