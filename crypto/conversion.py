import logging
from typing import Dict, Iterator, List, Optional, Tuple
from crypto.exchange import Exchange

from crypto.utils.types import Currency, CurrencyList, Pair

from .metadata import *

logger = logging.getLogger(__name__)


class Conversion:
    """
    Class used to add currency conversions to order json
    e.g. if orders contains BTCBUSD and BTCETH and target currency is USDT
    this class should be able to add prices in terms of BTCUSDT and BTCUSDT/ETHUSDT

    BTCETH transaction could be split into -> BTCUSDT & ETHUSDT
    """

    def __init__(self,
                 exchange: Exchange,
                 target_currency: Optional[Currency] = None):
        self.exchange = exchange()
        self.target_currency_list = target_currency
        self.available_currencies = self._available_currencies
        self.available_currency_pairs = self._available_currency_pairs
        # target_pairs
        # {'*original_pair*':
        #   [('*curr1*', '*curr2*'),
        #   '*target_pair*}

    @property
    def _available_currencies(self) -> List:
        return self.exchange.get_currency_list()
    
    @property
    def _available_currency_pairs(self) -> List:
        return self.exchange.get_currency_pair_list()

    def get_currencies_to_convert(self, currencies: CurrencyList) -> dict:
        """
        example input:
        [
            "BTCBUSD",
            "EURBUSD"
        ]
        example output:
        {
            'BTCBUSD': [('BTC', 'BUSD')],
            'EURBUSD': [('EUR', 'BUSD')]
        }
        """
        pairs_in_data = set(currencies)
        current_pair = {}
        for pair in pairs_in_data:
            current_pair.update(
                self.split_pair(pair)
            )
        return current_pair

    def _split_pair(self, pair: Pair) -> Optional[dict]:
        def _check_curr(_pair: str, _curr1: str) -> Optional[str]:
            _pair1 = _pair.removeprefix(_curr1).removesuffix(_curr1)
            if _pair != _pair1:
                return _pair1

        for curr_x in self.available_currencies:
            curr_y = _check_curr(pair, curr_x)
            if curr_y:
                for curr in self.available_currencies:
                    if curr == curr_y:
                        return {pair: [(curr_x, curr_y)]}

    def split_pair(self, pair: Pair) -> dict:
        """
        example input: "BTCBUSD"
        example output:
        {
            'EURBUSD': [('EUR', 'BUSD')]
        }
        """
        pairs = self._split_pair(pair)
        if pairs is None:
            raise
        return pairs

    def find_conversion_pair(self, current_pair: Tuple, target_currency: Currency) -> Pair:
        """
        Finds pair which can be used to convert currency pair to target currency
        Returns pair or none if not needed
        """
        def check_search_pair(*args):
            for arg in args:
                if arg in self.available_currency_pairs:
                    return arg

        if target_currency in current_pair:
            return None
        for curr in current_pair:
            search_pair1 = curr + target_currency
            search_pair2 = target_currency + curr

            pair = check_search_pair(search_pair1, search_pair2)
            if pair:
                return pair

    def add_conversion_pair(self, current_pair: dict, target_currency: Currency) -> dict:
        """
        Example input:
        current_pair =
        {
            'BTCBUSD': [('BTC', 'BUSD')],
            'EURBUSD': [('EUR', 'BUSD')]
        }
        target_currency = 'USDT'

        Example output:
        {
            'BTCBUSD': [('BTC', 'BUSD'), 'BTCUSDT'],
            'EURBUSD': [('EUR', 'BUSD'), 'EURUSDT']
        }
        """

        new_dict = {}
        for key, val in current_pair.items():
            _val = val
            _val.append(
                self.find_conversion_pair(val[0], target_currency)
            )
            new_dict[key] = _val
        return new_dict

    def create_currency_conversion_dict(self, currencies: CurrencyList, target_currency: Currency) -> dict:
        """
        example input:
        [
            "BTCBUSD",
            "EURBUSD"
        ]

        target_currency = 'USDT'
    
        example output:
        {
            'BTCBUSD': [('BTC', 'BUSD'), 'BTCUSDT'],
            'EURBUSD': [('EUR', 'BUSD'), 'EURUSDT']
        }
        """
        return self.add_conversion_pair(
            self.get_currencies_to_convert(currencies), target_currency
        )

    def get_conversion_price(self, target_currency_pair, date_time):
        return self.get_historical_klines(
            target_currency_pair, date_time, date_time+1)
