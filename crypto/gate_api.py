from typing import List
import logging
from typing import List
from gate_api import SpotApi
from .metadata import *
from crypto.utils.types import PairList

from .exchange import Exchange


log = logging.getLogger(__name__)

class GateAPI(Exchange):
    def __init_exchange(self):
        pass

    def get_currency_list(self):
        return self.list_currency_pairs()

    def get_pair_list(self):
        """
        Gets available download pairs based on CurrencyList target currency
        """
        NotImplementedError()

    def get_historical_klines(self, currency_pair, start, end, interval):
        """
        Should retrieve average price for given datetime and pair
        """
        NotImplementedError()
