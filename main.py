import asyncio
from binance import BinanceAPI
from services import BinanceTrader
from config import (
    API_URL,
    TESTNET_API_KEY,
    TESTNET_API_SECRET,
    SYMBOL,
    ORDER_AMOUNT_USDT,
    THRESOLD_PERCENTAGE,
    COOL_OFF_PERIOD,
)

if __name__ == "__main__":

    async def main():
        api = BinanceAPI(API_URL, TESTNET_API_KEY, TESTNET_API_SECRET)
        trader = BinanceTrader(
            api,
            SYMBOL,
            threshold_percentage=THRESOLD_PERCENTAGE,
            order_amount=ORDER_AMOUNT_USDT,
            cool_off_period=COOL_OFF_PERIOD,
        )
        try:
            await trader.run()
        finally:
            await trader.close()

    asyncio.run(main())
