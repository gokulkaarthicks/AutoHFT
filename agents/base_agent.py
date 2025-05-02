# agents/base_agent.py

class BaseAgent:
    def __init__(self, name, budget_usd, execution_manager, decision_engine):
        self.name = name
        self.budget_usd = budget_usd
        self.execution_manager = execution_manager
        self.decision_engine = decision_engine
        self.active_position = None

    async def act(self, market_snapshot):
        raise NotImplementedError

    async def shutdown(self):
        if self.active_position:
            await self.execution_manager.place_sell(self.active_position['quantity'])
            self.active_position = None