# runner.py

import argparse
import asyncio
import logging
from manager.agent_manager import AgentManager
from config.settings import KRAKEN_API_KEY, KRAKEN_API_SECRET

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--time", type=int, required=True, help="Trading duration in seconds")
    parser.add_argument("--amount", type=float, required=True, help="Total budget in USD")
    parser.add_argument("--split", type=float, default=100, help="Per-agent budget split (default 100 USD)")
    args = parser.parse_args()

    logging.info("Starting Kraken Futures Trading System (Demo/Test Mode).")

    manager = AgentManager(
        total_budget=args.amount,
        split_budget=args.split
    )
    await manager.start_trading(runtime_seconds=args.time)

if __name__ == "__main__":
    asyncio.run(main())