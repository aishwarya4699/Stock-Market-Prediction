from __future__ import annotations

from abc import ABC, abstractmethod

from numpy import array
from pandas import Series

from db_helper import connect_mongo
from helper import ModelHelper
from preproc import get_stock_data, get_train_data, get_train_test_data

connect_mongo()


class BaseModel(ABC):
    def __init__(
        self,
        symbol: str,
        days_of_data: int = 300,
        train_size: float = 1,
        scaler=None,
        is_keras: bool = False,
        save_model: bool = True
    ):
        self.model_helper = ModelHelper(type(self).__name__, symbol, is_keras)

        self.is_test_model = train_size != 1

        self.stock_data = get_stock_data(symbol, days_of_data)

        if self.is_test_model:
            self.train_data, self.test_data = get_train_test_data(symbol, days_of_data, train_size)

        else:
            self.train_data = get_train_data(symbol, days_of_data)
            self.test_data = None

        self.model = self.model_helper.get_model_from_mongo(self.train_data.index.max())

        self.scaler = scaler() if scaler else None
        self.save_model = save_model

    @abstractmethod
    def train(self) -> None:
        # self.model = train_model_here
        raise NotImplementedError

    def fit(self) -> BaseModel:
        if self.scaler:
            self.train_data = Series(self.scaler.fit_transform(
                self.train_data.values.reshape(-1, 1)).reshape(-1), index=self.train_data.index)

        if not self.model:
            self.train()
            if self.save_model:
                self.model_helper.save_model_to_mongo(
                    self.model, self.train_data.index.min(), self.train_data.index.max()
                )

        return self

    @abstractmethod
    def make_predictions(self, n_days: int) -> array:
        # return self.model.predict(n_days)
        raise NotImplementedError

    def predict(self, n_days: int = 0) -> Series:
        if not self.model:
            raise Exception("No Model Found")

        if n_days > 0:
            if self.is_test_model:
                raise Exception("Test Model. n_days is predefined. Call without the parameter")

        else:
            if not self.is_test_model:
                raise Exception("n_days should be a positive integer for non-test models")

            else:
                n_days = len(self.test_data)

        predictions = self.make_predictions(n_days)

        if self.scaler:
            predictions = self.scaler.inverse_transform(predictions)

        return predictions

    def fit_predict(self, n_days: int = 0) -> array:
        return self.fit().predict(n_days)
