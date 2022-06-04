import logging
from typing import List
from binance.client import Client

from .exchange import Exchange
from .metadata import *
from .utils import *


logger = logging.getLogger(__name__)


class BinanceAPI(Exchange):
    """
    Class encompassing all Binance API methods
    """

    def init_exchange(self):
        # Initiate exchange API
        self.exchangeAPI = Client(
            api_key=self.API_KEY,
            api_secret=self.SECRET_KEY
        )

        # Test connection
        self.exchangeAPI.ping()

    def __str__(self):
        return 'binance'

    def __repr__(self):
        return 'binance'

    def update_details(self):
        self.details['request_order_limit'] = 1000

    def get_currency_list(self):
        base_assets = set(self._get_listing_details('baseAsset'))
        quote_assets = set(self._get_listing_details('quoteAsset'))
        full_currency_list = list(base_assets.union(quote_assets))
        return full_currency_list

    def _get_listing_details(self, detail: str) -> set:
        """
        returns listing details
        """
        info = self.exchangeAPI.get_exchange_info()
        return set([e[detail] for e in info['symbols']])

    def get_currency_pair_list(self) -> PairList:
        download_pairs = self._get_listing_details(
            'symbol')
        # self.crypto_filter = list(self._get_listing_details(
        #     'baseAsset'))

        # download_pairs = self._filter_by_currency(
        #     self.all_available_pairs, self.crypto_filter)

        return list(download_pairs)

    def _filter_by_currency(self,
                            inp: PairList,
                            currency_filter: Currency | CurrencyList
                            ) -> CurrencyList:
        """
        Filters list of currency pairs by filter
        """
        # cannot use 'contains' e.g. 'CKBUSDT' contains BUSD but is not BUSD
        if isinstance(currency_filter, list):
            currency_filter = tuple(currency_filter, )
        return list(
            filter(
                lambda x: x.endswith(currency_filter)
                or x.startswith(currency_filter), inp
            )
        )

    @property
    def server_time(self) -> str:
        return self.exchangeAPI.time()["serverTime"]

    def get_historical_klines(self,
                              currency_pair,
                              start,
                              end,
                              interval='1m'
                              ) -> List:
        """
        returns list of binance klines with following format:
        [
          [
            1499040000000,      // Open time
            "0.01634790",       // Open
            "0.80000000",       // High
            "0.01575800",       // Low
            "0.01577100",       // Close
            "148976.11427815",  // Volume
            1499644799999,      // Close time
            "2434.19055334",    // Quote asset volume
            308,                // Number of trades
            "1756.87402397",    // Taker buy base asset volume
            "28.46694368",      // Taker buy quote asset volume
            "17928899.62484339" // Ignore.
          ]
        ]
        """
        return self.exchangeAPI.get_historical_klines(
            currency_pair, interval, start, end
        )

    def nonce(self):
        # TODO
        NotImplementedError()

    def get_orders_wo_limit(self,
                            limit,
                            crypto_pair: Crypto,
                            start_time: Optional[int]=None,
                            end_time: Optional[int]=None,
                            attempts=10
                            ) -> List:
        """
        Extends get_all_orders method which is limited to 1000 orders

        [
          {
            "symbol": "LTCBTC",
            "orderId": 1,
            "orderListId": -1, //Unless OCO, the value will always be -1
            "clientOrderId": "myOrder1",
            "price": "0.1",
            "origQty": "1.0",
            "executedQty": "0.0",
            "cummulativeQuoteQty": "0.0",
            "status": "NEW",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "stopPrice": "0.0",
            "icebergQty": "0.0",
            "time": 1499827319559,
            "updateTime": 1499827319559,
            "isWorking": true,
            "origQuoteOrderQty": "0.000000"
          }
        ]
        """

        orders = []
        @retry_wrapper(attempts, limit, False)
        def add_orders(_orders, _crypto_pair, _start, _end):
            if orders:
                start_time = int(_orders[-1]['time']) -1  # corresponds to ['time']
            else:
                start_time = _start

            resp = self.exchangeAPI.get_all_orders(
                    symbol=_crypto_pair,
                    startTime=start_time,
                    endTime=_end,
                    limit=limit)
            _orders.extend(resp)
            return len(resp)

        add_orders(orders, crypto_pair, start_time, end_time)
        return orders

    def _spot_download(self,
                       crypto_list: CurrencyList,
                       start_time: Optional[int]=None,
                       end_time: Optional[int]=None,
                       limit=1000
                       ):
        """
        Spot download function
        """
        # TODO IMPROVE - add rate limiter
        # download all orders and append response to list
        download_pairs = self.get_currency_pair_list()
        if crypto_list:
            download_pairs = self._filter_by_currency(
                download_pairs, crypto_list)

        idx = 0
        pair_orders = {}
        logger.info(f'Estimated download time: {len(download_pairs)//60} mins')

        for _crypto_pair in download_pairs:

            idx += 1
            _orders = self.get_orders_wo_limit(
                crypto_pair=_crypto_pair,
                start_time=start_time,
                end_time=end_time,
                limit=limit)

            pair_orders[_crypto_pair] = _orders

        return pair_orders

    def get_spot_trades(self,
                        crypto_list: CryptoList=[],
                        start_time=None,
                        end_time=None,
                        limit=1000
                        ) -> Dict:

        if not crypto_list:
            logger.warning('FULL DATASET SELECTED: EXPECT LONG DOWNLOAD TIME')

        return self._spot_download(crypto_list, start_time, end_time, limit)
