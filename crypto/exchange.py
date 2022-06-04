from abc import ABC, abstractmethod
import logging

from typing import Optional

from .metadata import *
from crypto.utils.types import *


log = logging.getLogger(__name__)


class Exchange(ABC):
    """
    The Exchange interface
    containing methods explicity used to retrieve and normalize
    exchange data
    """
    DATA_PATH = "data\\"  # TODO define externally

    def __init__(self,
                 API_KEY: Optional[str]=None,
                 SECRET_KEY: Optional[str]=None,
                 ) -> None:

        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY

        self.update_details()

        self.all_available_pairs: PairList = []

        self.init_exchange()

    @property
    def details(self) -> dict:
        """
        Returns exchange details
        """
        return {
            'request_order_limit': None
        }

    @abstractmethod
    def init_exchange(self, api_key, secret_key):
        pass

    @abstractmethod
    def update_details(self) -> None:
        """
        Adds exchange specific details
        """
        pass

    @abstractmethod
    def get_currency_list(self) -> CurrencyList:
        """
        Should retrieve list of all available crypto/fiat currencies
        """
        pass

    @abstractmethod
    def get_currency_pair_list(self) -> PairList:
        """
        Gets pairs to be downloaded based instance filters
        """
        pass

    @abstractmethod
    def get_historical_klines(self,
                              currency_pair: Pair,
                              start,
                              end,
                              interval: str
                              ) -> List:
        """
        Should retrieve average price for given datetime and pair
        """
        pass

    @abstractmethod
    def get_spot_trades(self,
                        crypto_filter: CurrencyList=[],
                        start_date=None,
                        end_date=None
                        ) -> List:
        """
        Returns list of all historical spot trades based on filter
        and date range 
        """
        pass
