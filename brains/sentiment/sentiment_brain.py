# brains/sentiment/sentiment_brain.py

import numpy as np
import random

class SentimentBrain:
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.price_history = []

        self.hidden_state = 0.0

        self.weight_price = random.uniform(0.8, 1.2)
        self.weight_bid_ask = random.uniform(0.8, 1.2)

    def update(self, mark_price: float, best_bid: float, best_ask: float):
        mid_price = (best_bid + best_ask) / 2
        price_diff = mark_price - mid_price

        self.hidden_state = 0.9 * self.hidden_state + 0.1 * (self.weight_price * mark_price + self.weight_bid_ask * price_diff)

        self.price_history.append(mark_price)
        if len(self.price_history) > self.window_size:
            self.price_history.pop(0)

    def predict_sentiment(self) -> str:
        if len(self.price_history) < 2:
            return "neutral"

        recent_trend = np.polyfit(range(len(self.price_history)), self.price_history, 1)[0]

        combined_signal = 0.5 * self.hidden_state + 0.5 * recent_trend

        if combined_signal > 0.05:
            return "bullish"
        elif combined_signal < -0.05:
            return "bearish"
        else:
            return "neutral"