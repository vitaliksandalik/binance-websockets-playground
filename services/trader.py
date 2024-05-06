from datetime import datetime, timedelta
from decimal import Decimal
from binance import StreamManager
from services.order_manager import OrderManager
from utils import Logger


class BinanceTrader:
    def __init__(
        self,
        api,
        symbol="BTCUSDT",
        threshold_percentage=0.01,
        cool_off_period=60,
        order_amount=20,
    ):
        self.api = api
        self.symbol = symbol
        self.threshold_percentage = Decimal(threshold_percentage)
        self.cool_off_period = cool_off_period
        self.order_amount = Decimal(order_amount)
        self.last_order_time = datetime.now() - timedelta(seconds=self.cool_off_period)
        self.logger = Logger("BinanceTraderLogger", "./data/binance_trader.log")
        self.stream_manager = StreamManager(api, self.logger, self.symbol)
        self.order_manager = OrderManager(
            api, self.logger, self.symbol, self.order_amount
        )

    async def run(self):
        await self.stream_manager.connect()
        await self.stream_manager.handle_messages(self.handle_message)

    async def handle_message(self, message):
        data_type, data = self.stream_manager.parse_message(message)
        if data_type == "order_book":
            await self.handle_order_book(data)
        elif data_type == "order_update":
            self.order_manager.handle_order_update(data)

    async def handle_order_book(self, data):
        spread_percentage = self.stream_manager.calculate_spread_percentage(data)

        if spread_percentage is not None:
            current_time = datetime.now()
            time_since_last_order = (
                current_time - self.last_order_time
            ).total_seconds()

            if (
                spread_percentage > self.threshold_percentage
                and time_since_last_order > self.cool_off_period
            ):
                self.logger.info(
                    f"Trading Opportunity Found! Spread is {spread_percentage:.2f}%"
                )
                await self.order_manager.place_trading_order(data, current_time)
                self.last_order_time = current_time
                self.logger.info("Going to cooldown.")
        # else:
        #     self.logger.info("No valid spread percentage calculated; check market conditions or data integrity.")

    async def close(self):
        await self.stream_manager.close()
        await self.api.close()
