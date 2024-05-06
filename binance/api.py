import aiohttp
import hmac
import hashlib
import time
from decimal import Decimal


class BinanceAPI:
    def __init__(self, api_url, api_key, api_secret):
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    def generate_signature(self, data):
        return hmac.new(self.api_secret, data.encode(), hashlib.sha256).hexdigest()

    async def authenticate(self):
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self.generate_signature(query_string)
        headers = {"X-MBX-APIKEY": self.api_key}
        url = f"{self.api_url}/api/v3/account?{query_string}&signature={signature}"
        async with self.session.get(url, headers=headers) as response:
            return await response.json()

    async def get_symbol_info(self, symbol):
        url = f"{self.api_url}/api/v3/exchangeInfo?symbol={symbol}"
        async with self.session.get(url) as response:
            info = await response.json()
            filters = {
                item["filterType"]: item for item in info["symbols"][0]["filters"]
            }
            return filters["LOT_SIZE"]

    async def get_latest_price(self, symbol):
        url = f"{self.api_url}/api/v3/ticker/price?symbol={symbol}"
        async with self.session.get(url) as response:
            return Decimal((await response.json())["price"])

    async def place_order(self, symbol, side, quantity, price):
        timestamp = int(time.time() * 1000)
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": quantity,
            "price": price,
            "timestamp": timestamp,
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = self.generate_signature(query_string)
        headers = {"X-MBX-APIKEY": self.api_key}
        url = f"{self.api_url}/api/v3/order?{query_string}&signature={signature}"
        async with self.session.post(url, headers=headers) as response:
            return await response.json()

    async def start_user_data_stream(self):
        url = f"{self.api_url}/api/v3/userDataStream"
        headers = {"X-MBX-APIKEY": self.api_key}
        async with self.session.post(url, headers=headers) as response:
            return (await response.json())["listenKey"]
