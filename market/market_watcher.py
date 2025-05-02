# market/market_watcher.py

import aiohttp
import asyncio
import json
from config.settings import BASE_URL, SYMBOL, PRODUCTION_MODE

class MarketWatcher:
    def __init__(self):
        self.session = None
        self.ws = None
        self.latest_mark_price = None

    async def connect(self):
        self.session = aiohttp.ClientSession()

        if PRODUCTION_MODE:
            ws_url = "wss://futures.kraken.com/ws/v1"
        else:
            ws_url = "wss://demo-futures.kraken.com/ws/v1"

        self.ws = await self.session.ws_connect(ws_url)
        print(f"Connected to Kraken Futures WebSocket.")

        payload = {
            "event": "subscribe",
            "feed": "ticker",
            "product_ids": [SYMBOL]
        }
        await self.ws.send_json(payload)

        asyncio.create_task(self._listen())

    async def _listen(self):
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if isinstance(data, dict) and data.get("feed") == "ticker":
                    bid = float(data.get("bid", 0))
                    ask = float(data.get("ask", 0))
                    if bid and ask:
                        self.latest_mark_price = (bid + ask) / 2

    async def get_mark_price(self):
        retries = 5
        while self.latest_mark_price is None and retries > 0:
            await asyncio.sleep(0.1)
            retries -= 1

        return self.latest_mark_price

    async def close(self):
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()