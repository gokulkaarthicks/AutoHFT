# execution/execution_manager.py

import aiohttp
import time
import hmac
import hashlib
import base64
import urllib.parse
import logging
import asyncio
from config.settings import KRAKEN_API_KEY, KRAKEN_API_SECRET, BASE_URL, SYMBOL, TICK_SIZE, QUANTITY_PRECISION

class ExecutionManager:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.logger = logging.getLogger(__name__)

    async def _sign_request(self, endpoint, data):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = endpoint.encode() + hashlib.sha256(encoded).digest()
        signature = hmac.new(base64.b64decode(KRAKEN_API_SECRET), message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())
        return sigdigest.decode()

    async def _send_signed_request(self, endpoint, data):
        url = f"{BASE_URL}{endpoint}"
        headers = {
            'APIKey': KRAKEN_API_KEY,
            'API-Sign': await self._sign_request(endpoint, data)
        }

        async with self.session.post(url, headers=headers, data=data) as resp:
            res = await resp.json()
            return res

    async def get_mark_price(self):
        url = f"{BASE_URL}/tickers"
        async with self.session.get(url) as resp:
            data = await resp.json()
            result = data.get('tickers', [])
            for ticker in result:
                if ticker['symbol'] == SYMBOL:
                    return float(ticker['last'])
            return None

    async def place_buy(self, budget_usd, retries=3):
        for attempt in range(retries):
            mark_price = await self.get_mark_price()
            if not mark_price:
                await asyncio.sleep(0.5)
                continue

            qty = round(budget_usd / mark_price, QUANTITY_PRECISION)

            data = {
                'nonce': int(time.time() * 1000),
                'orderType': 'lmt',
                'side': 'buy',
                'size': qty,
                'limitPrice': f"{mark_price * 0.999:.2f}",
                'symbol': SYMBOL
            }

            res = await self._send_signed_request('/sendorder', data)
            if res and res.get('result') == 'success':
                return mark_price, qty

            self.logger.error(f"Buy attempt {attempt + 1} failed. Retrying...")
            await asyncio.sleep(0.5)

        self.logger.error("All retries failed for Buy order.")
        return None, None

    async def place_sell(self, quantity, retries=3):
        for attempt in range(retries):
            mark_price = await self.get_mark_price()
            if not mark_price:
                await asyncio.sleep(0.5)
                continue

            data = {
                'nonce': int(time.time() * 1000),
                'orderType': 'lmt',
                'side': 'sell',
                'size': quantity,
                'limitPrice': f"{mark_price * 1.001:.2f}",
                'symbol': SYMBOL
            }

            res = await self._send_signed_request('/sendorder', data)
            if res and res.get('result') == 'success':
                return True

            self.logger.error(f"Sell attempt {attempt + 1} failed. Retrying...")
            await asyncio.sleep(0.5)

        self.logger.error("All retries failed for Sell order.")
        return False

    async def force_market_sell(self, quantity):
        data = {
            'nonce': int(time.time() * 1000),
            'orderType': 'mkt',
            'side': 'sell',
            'size': quantity,
            'symbol': SYMBOL
        }
        res = await self._send_signed_request('/sendorder', data)
        if res and res.get('result') == 'success':
            self.logger.warning("Forced MARKET SELL executed.")
            return True
        return False

    async def close(self):
        if self.session:
            await self.session.close()