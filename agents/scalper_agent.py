# agents/scalper_agent.py

import random
from brains.heuristic_brain import HeuristicBrain
from brains.ml_brain import MLBrain
from brains.rl_brain import RLBrain

class ScalperAgent:
    def __init__(self, name, budget_usd, execution_manager, brain_type, pnl_monitor):
        self.name = name
        self.initial_budget = budget_usd
        self.wallet = budget_usd
        self.execution_manager = execution_manager
        self.pnl_monitor = pnl_monitor
        self.active_position = None

        if brain_type == "heuristic":
            self.brain = HeuristicBrain()
        elif brain_type == "ml":
            self.brain = MLBrain()
        elif brain_type == "rl":
            self.brain = RLBrain()
        else:
            raise ValueError(f"Unknown brain type: {brain_type}")

    async def act(self, market_snapshot):
        if self.wallet <= 0:
            return

        mark_price = float(market_snapshot['markPrice'])

        if not self.active_position:
            if self.brain.should_buy(market_snapshot):
                buy_budget = random.uniform(0.1, 0.3) * self.wallet

                entry_price, quantity = await self.execution_manager.place_buy(buy_budget)
                if entry_price and quantity:
                    self.wallet -= buy_budget
                    self.active_position = {
                        'entry_price': entry_price,
                        'quantity': quantity,
                        'used_budget': buy_budget
                    }
                    print(f"[{self.name}] Bought at {entry_price} (qty {quantity})")

        else:
            entry_price = self.active_position['entry_price']
            quantity = self.active_position['quantity']
            used_budget = self.active_position['used_budget']

            target_price = entry_price * 1.001

            if mark_price >= target_price or self.brain.should_sell(entry_price, mark_price):
                sell_success = await self.execution_manager.place_sell(quantity)
                if sell_success:
                    profit = (mark_price - entry_price) * quantity
                    await self.pnl_monitor.add_profit(profit)
                    self.wallet += used_budget + profit
                    print(f"[{self.name}] Sold at {mark_price} | Profit: {profit:.4f} USD")
                    self.active_position = None
                else:
                    print(f"[{self.name}] Sell attempt failed, retrying later...")

    async def shutdown(self):
        if self.active_position:
            quantity = self.active_position['quantity']
            success = await self.execution_manager.force_market_sell(quantity)
            if success:
                mark_price = await self.execution_manager.get_mark_price()
                if mark_price:
                    profit = (mark_price - self.active_position['entry_price']) * quantity
                    await self.pnl_monitor.add_profit(profit)
                    print(f"[{self.name}] Emergency sold during shutdown, profit: {profit:.4f}")
            self.active_position = None