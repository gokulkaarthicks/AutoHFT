# manager/pnl_monitor.py

import asyncio

class PnLMonitor:
    def __init__(self):
        self.total_profit = 0.0
        self._lock = asyncio.Lock()

    async def add_profit(self, profit):
        async with self._lock:
            self.total_profit += profit

    async def subtract_loss(self, loss):
        async with self._lock:
            self.total_profit -= loss

    async def reset(self):
        async with self._lock:
            self.total_profit = 0.0

    def get_total_profit(self):
        return self.total_profit