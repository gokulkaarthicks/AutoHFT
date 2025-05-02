# brains/heuristic_brain.py

import random
import numpy as np

class HeuristicBrain:
    def __init__(self):
        self.volatility_window = []
        self.window_size = 20
        self.spread_threshold = 0.0007  # 0.07%
        self.min_profit_target = 0.0005  # 0.05%

    def update_volatility(self, mark_price):
        self.volatility_window.append(mark_price)
        if len(self.volatility_window) > self.window_size:
            self.volatility_window.pop(0)

    def estimate_volatility(self):
        if len(self.volatility_window) < 2:
            return 0.0
        return np.std(self.volatility_window) / np.mean(self.volatility_window)

    def should_buy(self, market_snapshot: dict) -> bool:
        mark_price = float(market_snapshot['markPrice'])
        self.update_volatility(mark_price)

        spread = self.calculate_spread(mark_price)
        volatility = self.estimate_volatility()
        sentiment = market_snapshot.get('sentiment', 'neutral')

        if sentiment == 'bullish':
            if spread > 0.0001 or volatility > 0.0002:
                return True
            return random.random() < 0.3

        elif sentiment == 'neutral':
            if spread > 0.0002 and volatility > 0.0003:
                return True
            return random.random() < 0.1

        elif sentiment == 'bearish':
            return False

        return False

    def should_sell(self, entry_price: float, current_price: float) -> bool:
        profit_ratio = (current_price - entry_price) / entry_price
        return profit_ratio >= self.min_profit_target

    def calculate_spread(self, mark_price: float) -> float:
        simulated_bid = mark_price * 0.9995
        simulated_ask = mark_price * 1.0005
        return (simulated_ask - simulated_bid) / simulated_bid