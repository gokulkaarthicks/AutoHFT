# manager/agent_manager.py

import asyncio
import random
import logging
from agents.scalper_agent import ScalperAgent
from manager.execution_manager import ExecutionManager
from market.market_watcher import MarketWatcher
from manager.pnl_monitor import PnLMonitor

class AgentManager:
    def __init__(self, total_budget, split_budget):
        self.total_budget = total_budget
        self.split_budget = split_budget
        self.agents = []
        self.tasks = set()
        self.market_watcher = MarketWatcher()
        self.execution_manager = ExecutionManager()
        self.pnl_monitor = PnLMonitor()
        self.start_time = None
        self.rebalance_interval = 30  # seconds
        self.clone_interval = 60 # seconds
        self.last_rebalance = 0
        self.last_clone = 0
        self.peak_profit = 0.0

    async def initialize_agents(self):
        splits = int(self.total_budget / self.split_budget)
        logging.info(f"Spawning {splits} ScalperAgents...")

        brain_choices = ["heuristic", "ml", "rl"]

        for idx in range(splits):
            brain_type = random.choice(brain_choices)
            agent = ScalperAgent(
                name=f"ScalperAgent-{idx}",
                budget_usd=self.split_budget,
                execution_manager=self.execution_manager,
                brain_type=brain_type,
                pnl_monitor=self.pnl_monitor
            )
            self.agents.append(agent)
            logging.info(f"Initialized {agent.name} with brain type: {brain_type}")

    async def start_trading(self, runtime_seconds):
        await self.market_watcher.connect()
        await self.initialize_agents()

        self.start_time = asyncio.get_event_loop().time()
        logging.info(f"Starting trading for {runtime_seconds} seconds.")

        while (asyncio.get_event_loop().time() - self.start_time) < runtime_seconds:
            try:
                market_snapshot = await self.market_watcher.get_mark_price()
                snapshot = {'markPrice': float(market_snapshot)}

                for agent in self.agents:
                    task = asyncio.create_task(agent.act(snapshot))
                    self.tasks.add(task)
                    task.add_done_callback(self.tasks.discard)

                await self._rebalance_agents()
                await self._clone_agents()
                await self._check_global_protection()

                await asyncio.sleep(0.1)

            except Exception as e:
                logging.error(f"Main loop error: {e}")

        logging.info("Stopping agents...")
        await self.stop_all()

    async def _rebalance_agents(self):
        now = asyncio.get_event_loop().time()
        if now - self.last_rebalance > self.rebalance_interval:
            self.last_rebalance = now
            total_wallet = sum(agent.wallet for agent in self.agents)
            if total_wallet == 0:
                return

            for agent in self.agents:
                agent.wallet = (agent.wallet / total_wallet) * self.total_budget

            logging.info("Rebalanced agent wallets based on performance.")

    async def _clone_agents(self):
        now = asyncio.get_event_loop().time()
        if now - self.last_clone > self.clone_interval:
            self.last_clone = now
            clones = []
            for agent in self.agents:
                if agent.wallet >= 1.2 * agent.initial_budget:
                    clone_budget = (agent.wallet - agent.initial_budget) / 2
                    agent.wallet -= clone_budget
                    clone = ScalperAgent(
                        name=f"{agent.name}_clone",
                        budget_usd=clone_budget,
                        execution_manager=self.execution_manager,
                        brain_type=agent.brain_type,
                        pnl_monitor=self.pnl_monitor
                    )
                    clones.append(clone)
                    logging.info(f"Agent {agent.name} cloned successfully!")

            self.agents.extend(clones)

    async def _check_global_protection(self):
        current_profit = self.pnl_monitor.get_total_profit()
        if current_profit > self.peak_profit:
            self.peak_profit = current_profit

        if self.peak_profit > 0 and current_profit < self.peak_profit * 0.9:
            logging.warning("PnL dropped >10% from peak. Triggering STOP for all agents.")
            await self.stop_all()

    async def stop_all(self):
        for agent in self.agents:
            await agent.shutdown()

        if self.tasks:
            await asyncio.gather(*self.tasks)

        await self.market_watcher.close()

        logging.info(f"TOTAL FINAL PNL: {self.pnl_monitor.get_total_profit():.4f} USD")