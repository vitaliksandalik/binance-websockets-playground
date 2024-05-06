from decimal import Decimal
import json
import os


class OrderManager:
    def __init__(self, api, logger, symbol, order_amount):
        self.api = api
        self.logger = logger
        self.symbol = symbol
        self.order_amount = order_amount

    async def place_trading_order(self, order_book_data, current_time):
        highest_bid = Decimal(order_book_data["b"][0][0])
        lowest_ask = Decimal(order_book_data["a"][0][0])

        order_price = (highest_bid + lowest_ask) / Decimal(2)
        order_type = "BUY"  # Simplified strategy: always buy

        quantity = self.order_amount / order_price

        lot_size_info = await self.api.get_symbol_info(self.symbol)
        formatted_quantity = self.format_quantity(quantity, lot_size_info)

        order_response = await self.api.place_order(
            self.symbol, order_type, str(formatted_quantity), str(order_price)
        )
        await self.append_order_to_json(order_response, current_time)

        # self.logger.info(f"Placed order: {order_response}")

    def format_quantity(self, quantity, lot_size_info):
        step_size = Decimal(lot_size_info["stepSize"])
        min_qty = Decimal(lot_size_info["minQty"])
        max_qty = Decimal(lot_size_info["maxQty"])

        quantity = (quantity // step_size) * step_size

        if quantity < min_qty:
            quantity = min_qty
        if quantity > max_qty:
            quantity = max_qty

        return quantity

    async def append_order_to_json(self, new_order, current_time):
        file_path = "./data/orders.json"

        if "orderId" not in new_order:
            # self.logger.error("Attempted to append an order without an orderId.")
            return

        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            orders = []
        else:
            with open(file_path, "r") as file:
                try:
                    orders = json.load(file)
                except json.JSONDecodeError:
                    # self.logger.error("Failed to decode orders from JSON file. Starting fresh.")
                    orders = []

        new_order["timestamp"] = current_time.isoformat()
        orders.append(new_order)

        with open(file_path, "w") as file:
            json.dump(orders, file, indent=4)

        # self.logger.info(f"Order recorded: {new_order['orderId']} at {new_order['timestamp']}")

    def handle_order_update(self, order_data):

        symbol = order_data["s"]
        side = order_data["S"]
        order_price = order_data["p"]
        order_status = order_data["X"]

        self.logger.info(
            f"Order Update: {symbol} {side} at {order_price} status {order_status}"
        )
