# brains/rl/rl_brain.py

import random
import numpy as np

class RLBrain:
    def __init__(self, actions=('buy', 'sell', 'hold'), learning_rate=0.01, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.995):
        self.actions = actions
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay

    def _get_state_key(self, market_snapshot):
        try:
            price = float(market_snapshot.get('markPrice', 0))
            state = (round(price, 2),)
            return state
        except Exception as e:
            print(f"State key error: {e}")
            return (0,)

    def choose_action(self, market_snapshot):
        state_key = self._get_state_key(market_snapshot)

        if random.random() < self.exploration_rate:
            return random.choice(self.actions)
        else:
            q_values = self.q_table.get(state_key, [0] * len(self.actions))
            max_index = int(np.argmax(q_values))
            return self.actions[max_index]

    def update(self, current_snapshot, action, reward, next_snapshot):
        state_key = self._get_state_key(current_snapshot)
        next_state_key = self._get_state_key(next_snapshot)

        if state_key not in self.q_table:
            self.q_table[state_key] = [0] * len(self.actions)

        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = [0] * len(self.actions)

        action_index = self.actions.index(action)
        current_q = self.q_table[state_key][action_index]
        next_max_q = max(self.q_table[next_state_key])

        new_q = (1 - self.learning_rate) * current_q + self.learning_rate * (reward + self.discount_factor * next_max_q)
        self.q_table[state_key][action_index] = new_q

        self.exploration_rate = max(0.01, self.exploration_rate * self.exploration_decay)

    def should_buy(self, market_snapshot: dict) -> bool:
        action = self.choose_action(market_snapshot)
        return action == "buy"

    def should_sell(self, entry_price: float, current_price: float) -> bool:
        profit_ratio = (current_price - entry_price) / entry_price
        return profit_ratio >= 0.001