# brains/ml_brain.py

import numpy as np
from sklearn.linear_model import LogisticRegression
import random

class MLBrain:
    def __init__(self):
        self.window_size = 10
        self.price_history = []
        self.model = LogisticRegression()

        X = np.random.rand(100, self.window_size)
        y = np.random.randint(0, 2, 100)
        self.model.fit(X, y)

    def update_price_history(self, price: float):
        self.price_history.append(price)
        if len(self.price_history) > self.window_size:
            self.price_history.pop(0)

    def should_buy(self, market_snapshot: dict) -> bool:
        try:
            price = float(market_snapshot['markPrice'])
            self.update_price_history(price)

            if len(self.price_history) < self.window_size:
                return random.random() < 0.5

            input_features = np.array(self.price_history).reshape(1, -1)
            prediction = self.model.predict(input_features)[0]
            return prediction == 1
        except Exception as e:
            print(f"MLBrain prediction error: {e}")
            return random.random() < 0.5

    def should_sell(self, entry_price: float, current_price: float) -> bool:
        profit_ratio = (current_price - entry_price) / entry_price
        return profit_ratio >= 0.0005

    def dynamic_target_profit(self, entry_price: float) -> float:
        return round(entry_price * 1.0015, 2)