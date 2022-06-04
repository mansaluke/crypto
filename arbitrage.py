import time
import winsound
import ccxt
from ccxt.base.exchange import Exchange
# import ccxt.async_support as ccxt

frequency = 1000
duration = 2000


class ExchangeManager:
    def __init__(self, exchange: Exchange):
        self.exchange = exchange()
        self.ticker = {}

    def get_price(self, currency):
        self.ticker = self.exchange.fetch_ticker(currency)
        return self.ticker['ask']


class ExchangeOrders(ExchangeManager):
    inst_tracker = []

    def __new__(cls, exchange_id):
        cls.inst_tracker.append(exchange_id)
        return super(ExchangeOrders, cls).__new__(cls)

    def __init__(self, exchange_id):
        self.exchange_id = exchange_id
        self.exchange_class = getattr(ccxt, exchange_id)
        super().__init__(self.exchange_class)
        self.best_bid, self.best_ask = None, None

    def get(self, currency):
        self.get_price(currency)
        self.best_bid = self.ticker['best_bid']
        self.best_ask = self.ticker['best_ask']


class Arbitrage:

    exchange_list = [
        'binance',
        'kucoin',
        'gateio',
        'bitmart'
    ]

    def __init__(self, currency):

        self.currency = currency
        self.price_dictionary = {}

    def calc_opportunity(self):
        for exchange_id in self.exchange_list:
            exchange_class = getattr(ccxt, exchange_id)
            _currency = self.currency
            if exchange_id == 'binance':
                _currency = _currency.replace('/', '')

            try:
                self.price_dictionary[exchange_id] = ExchangeManager(
                    exchange_class).get_price(
                        _currency
                    )
            except:
                print(f'could not get {exchange_id}')

        self.max_price_exchange = max(self.price_dictionary, key=self.price_dictionary.get)
        self.max_price = self.price_dictionary[self.max_price_exchange]
        self.min_price_exchange = min(self.price_dictionary, key=self.price_dictionary.get)
        self.min_price = self.price_dictionary[self.min_price_exchange]
        self.percentage_diff = (self.max_price - self.min_price)/ self.min_price * 100

        print('{5} Percentage diff: {0}, {1}: {2}, {3}: {4}'.format(
            self.percentage_diff, self.max_price_exchange, self.max_price,
            self.min_price_exchange, self.min_price, self.currency
        ))

    def calculate_opportunity_dev(self):
        for exchange_id in self.exchange_list:
            exchange_orders = ExchangeOrders(exchange_id)

            _currency = self.currency
            if exchange_id == 'binance':
                _currency = _currency.replace('/', '')

            try:
                self.price_dictionary[exchange_id] = exchange_orders.get(
                    self.currency)
            except Exception as e:
                print(f'could not get {exchange_id}. Error: {e}')
        




PAIRS = [
    'BTC/USDT',
    'ETH/USDT',
    'SOL/USDT',
    'MATIC/USDT',
    'AVAX/USDT',
    'BNB/USDT',
    'HOT/USDT',
    'ADA/USDT',
    'VET/USDT',
    'LUNA/USDT',
    'MANA/USDT',
    'SAND/USDT',
    'DOT/USDT',
    'FTM/USDT',
    # 'UOS/USDT',
    'HBAR/USDT',
    'IOTX/USDT',
    'CRO/USDT',
    'ENJ/USDT',
    'VET/USDT',
    'PYR/USDT',
    'BOSON/USDT',
    'THETA/USDT',
    'DAG/USDT',
    'BEPRO/USDT',
    # 'XCUR/USDT', ONLY ERC20
    'KLV/USDT',
    'XPR/USDT',
    # 'UDO/USDT', ONLY ERC20
    'ONE/USDT',
    'ATOM/USDT',
    # 'SFUND/USDT', # BSC AND MIN SALE GATE: 5 UNITS
    'ALGO/USDT'
]
# ARWEAVE AND ELROND - HIGH TRANSACTION FEES: >$20


if __name__=="__main__":
    while True:
        for pair in PAIRS:
            try:
                a = Arbitrage(pair)
                a.calc_opportunity()
                if a.percentage_diff>3:
                    winsound.Beep(frequency, duration)
                    print('HERE!!!!!')
                    time.sleep(60)
            except Exception as e:
                print(f'FATAL ERROR: {e}')
        # time.sleep(30)
