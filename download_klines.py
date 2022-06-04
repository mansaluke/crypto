import logging
import time
import json
from crypto.binance_api import BinanceAPI
from secret import API_KEY, SECRET_KEY

# Set up logging
# logging.getLogger('crypto').propagate = False
logging.basicConfig(level=10)

a = time.strftime("%Y%m%d-%H%M%S")
d = BinanceAPI(API_KEY, SECRET_KEY)
out = d.get_historical_klines('BTCBUSD', "2022/01/01", "2022/01/01 10:00")

filename = 'data/klines.json'
with open(filename, 'w') as f:
    json.dump(out, f)

b = time.strftime("%Y%m%d-%H%M%S")
print(f'Download starting time: {a} Download finishing time: {b}')
