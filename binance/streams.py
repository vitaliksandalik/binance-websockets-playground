import json
from decimal import Decimal
import websockets
from config import WS_URL


class StreamManager:
    def __init__(self, api, logger, symbol):
        self.api = api
        self.logger = logger
        self.symbol = symbol
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(WS_URL)
        await self.subscribe_to_streams()

    async def subscribe_to_streams(self):
        order_book_stream = f"{self.symbol.lower()}@depth"
        user_stream = await self.api.start_user_data_stream()
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [order_book_stream, f"{user_stream}"],
            "id": 1,
        }
        await self.ws.send(json.dumps(subscribe_message))
        self.logger.info("Subscribed to Order Book and User Data Stream.")

    async def handle_messages(self, message_handler):
        async for message in self.ws:
            await message_handler(message)

    def parse_message(self, message):
        data = json.loads(message)
        event_type = data.get("e")

        if event_type == "depthUpdate":
            return "order_book", data

        elif event_type == "executionReport":
            return "order_update", data
        else:
            # self.logger.info(f"Received unhandled message type: {event_type}")
            return None, None

    def calculate_spread_percentage(self, order_book_data):
        if not order_book_data["b"] or not order_book_data["a"]:
            # self.logger.info("No bids or asks in the order book snapshot.")
            return None

        highest_bid = Decimal(order_book_data["b"][0][0])
        lowest_ask = Decimal(order_book_data["a"][0][0])

        if highest_bid == 0 or lowest_ask == 0:
            self.logger.error(
                "One of the necessary price points is zero, which is not expected."
            )
            return None

        spread_percentage = (
            (lowest_ask - highest_bid) / ((lowest_ask + highest_bid) / 2)
        ) * Decimal(100)
        return spread_percentage

    async def close(self):
        await self.ws.close()
