from dotenv import load_dotenv
import os

load_dotenv()

TESTNET_API_KEY = os.getenv("TESTNET_API_KEY")
TESTNET_API_SECRET = os.getenv("TESTNET_API_SECRET")
WS_URL = "wss://testnet.binance.vision/ws"
API_URL = "https://testnet.binance.vision"
SYMBOL = "BTCUSDT"
ORDER_AMOUNT_USDT = 10
THRESOLD_PERCENTAGE = 0.01
COOL_OFF_PERIOD = 60
