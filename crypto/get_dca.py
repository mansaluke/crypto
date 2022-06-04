from binance.client import Client
import time
from typing import List, AnyStr, Iterable
from ...secret import KEY, SECRET
from .utils import milliseconds_to_date

##### DEPRECATED ######


def get_historical_price(client: Client(), currency_pair, start_str):
    """
    gets historical opening price at closest minute
    """
    kline = client.get_klines(
        symbol=currency_pair,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        startTime=start_str,
        endTime=start_str+60000)
    return {'date': milliseconds_to_date(kline[0][0]), 'price': kline[0][1]}



client = Client(KEY, SECRET)
exchange_info = client.get_exchange_info()


class DCA():
    def __init__(
        self,
        coins: List=None,
        target_currency: AnyStr='USDT',
        startTime=None,
        endTime=None):
        """
        if no start or endtime is specified then the default is used.
        if CSVs already exist then the corresponding timestamp is used as a startTime
        """

        self.quote_assets = self.get_exchange_info('quoteAsset')
        assert target_currency in self.quote_assets

        if coins:
            assert isinstance(coins, list)

        # get full coin list
        self.full_pair_list: Iterable = self.get_exchange_info('symbol')  # remove list()
        self.coin_list: Iterable = coins or self.get_exchange_info('baseAsset')
        self.target_currency: str = target_currency

        self.startTime: int = startTime
        if endTime:
            self.endTime: int = endTime


        self.pair_orders = []

    def download(self):
        for _coin in self.coin_list:
            if _coin != self.target_currency:
                _orders = []
                self.pairs: list = self.filter_by_currency(
                    self.full_pair_list, _coin)

                print(f'Downloading for: {_coin} \n' +
                      f'Estimated download time: {len(self.pairs)} seconds')
                # downloading all orders
                idx = 0
                for i in self.pairs:
                    idx += 1
                    _orders.extend(
                        client.get_all_orders(
                            symbol=i,
                            startTime=self.startTime,
                            endTime=self.endTime)
                        )
                    if idx % 3 == 0:
                        time.sleep(1)
                    if idx == 199:
                        time.sleep(60)

                print('Finished download')
                # get currency list (currency coin was bought in)
                # all pairs with orders assigned
                coin_set: set = set([o['symbol'] for o in _orders])
                coin_list = self.filter_by_currency(coin_set, _coin)
                current_currency_list: list = list(
                    map(lambda p: p.replace(_coin, ''), coin_list))

                self.target_currency_list = self.filter_by_currency(
                    self.full_pair_list, self.target_currency)

                print(f'Adding target currency to: {_coin}')
                # use to get target currency
                _orders = self.get_target_currency_pair(
                    _orders, _coin, current_currency_list)
                if _orders:
                    self.pair_orders.extend(_orders)

    def get_exchange_info(self, name):
        return set([e[name] for e in exchange_info['symbols']])

    def filter_by_currency(self, inp, currency_filter) -> List:
        # cannot use 'contains' e.g. 'CKBUSDT' contains BUSD but is not BUSD
        if isinstance(currency_filter, str):
            return list(
                filter(
                    lambda x: x.endswith(currency_filter)
                    or x.startswith(currency_filter), inp))
        else:
            return list(
                filter(
                    lambda x: x.endswith(tuple(currency_filter, ))
                    or x.startswith(tuple(currency_filter, )), inp))
                    
    def get_target_currency_pair(self, orders, coin, current_currency_list) -> List:
        # get current to target currency pair
        final_convertion_dict = {}
        found_target = True
        _target_pair = ''

        for c in current_currency_list:
            if c == self.target_currency:
                final_convertion_dict[c] = c
            else:
                # find single currency - test possibilities
                # e.g. usdtbusd or busdusdt
                _target_pair = c + self.target_currency

                if _target_pair in self.target_currency_list:
                    position = 1
                else:
                    _target_pair = self.target_currency + c
                    if _target_pair in self.target_currency_list:
                        position = 2
                    else:
                        print(
                            f'WARNING COULD NOT FIND {self.target_currency + c}')
                        found_target = False
            if found_target:
                final_convertion_dict[c] = _target_pair

        if found_target:
            for order in orders:
                if order['status'] != 'CANCELED':  # TODO add if buy?
                    _symbol = order['symbol'].replace(coin, '')
                    if _symbol == self.target_currency:
                        order['conversion_pair'] = 'NA'
                        order['target_currency_price'] = 1
                        order['target_price'] = float(order['price'])
                        order['target_pair'] = order['symbol']
                    else:
                        print(
                            final_convertion_dict[_symbol], order['updateTime'])
                        order['conversion_pair'] = final_convertion_dict[_symbol]
                        target_currency_price = get_historical_price(
                            client,
                            final_convertion_dict[_symbol],
                            order['updateTime'])
                        order['target_currency_price'] = target_currency_price['price']
                        if position == 1:
                            order['target_price'] = \
                                float(order['price']) * \
                                float(order['target_currency_price'])
                        else:
                            order['target_price'] = \
                                float(order['price']) / \
                                float(order['target_currency_price'])
                        order['target_pair'] = coin + self.target_currency
        return orders

    def save(self):
        import json
        with open(f'data/data_{time.strftime("%Y%m%d-%H%M%S")}.json', 'w') as outfile:
            json.dump(self.pair_orders, outfile)

