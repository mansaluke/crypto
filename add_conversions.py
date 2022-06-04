import json
import logging
from crypto.binance_api import BinanceAPI
from crypto.conversion import Conversion

logging.basicConfig(level=10)

file_path = 'data/test.json'

with open(file_path) as f:
    data = json.load(f)

print(data)

converter = Conversion(BinanceAPI)
out = converter.get_currencies_to_convert(data.keys())

a = converter.create_currency_conversion_dict(out, 'USDT')
