from helper import get_next_n_trading_days
import numpy as np
import pandas as pd
from numpy import array
from sklearn.svm import SVR

from base_model import BaseModel


class SVM(BaseModel):
    window = 14

    def train(self) -> None:
        X = np.array(pd.to_numeric(self.train_data.index))
        y = self.train_data.values
        X_train = X.reshape(-1, 1)
        y_train = y.reshape(-1, 1)

        self.model = model = SVR(
            kernel="rbf",
            C=1e3,
            verbose=True,
        )
        model.fit(X_train, y_train)

    def make_predictions(self, n_days: int) -> array:
        if not self.is_test_model:
            self.test_data = pd.Series(index=get_next_n_trading_days(n_days), dtype="float64")
        X = np.array(pd.to_numeric(self.test_data.index))
        X_test = X.reshape(-1, 1)

        return self.model.predict(X_test)
