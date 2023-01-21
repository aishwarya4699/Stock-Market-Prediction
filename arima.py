from numpy import array
from pmdarima.arima import auto_arima

from base_model import BaseModel


class ARIMA(BaseModel):
    def train(self) -> None:
        self.model = auto_arima(
            self.train_data,
            d=None,
            start_p=0,
            start_q=0,
            max_p=3,
            max_q=3,
            D=0,
            start_P=0,
            m=1,
            seasonal=False,
            error_action="ignore",
            trace=True,
            suppress_warnings=True,
            stepwise=True,
            test="adf",
            n_fits=30,
        )

    def make_predictions(self, n_days: int) -> array:
        return self.model.predict(n_periods=n_days)
