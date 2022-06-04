import pytest
from crypto.exchange_apis import BinanceAPI
from crypto.utils.types import CurrencyList


class BinanceAPIMock:
    def __init__(self):
        self.calls = {}

    def get_all_orders(self, **params):
        """
        first call returns limit number of orders, then 1.
        """
        symbol = params.get('symbol', "BTCUSD")
        limit = params.get('limit', 10)
        print(f'Getting orders for symbol: {symbol}')
        if symbol not in self.calls:
            self.calls[symbol] = 0
        self.calls[symbol] += 1
        if self.calls[symbol] == 1:
            return self.create_mock_orders(limit, symbol)
        return self.create_mock_orders(1, symbol)

    def create_mock_orders(self, size: int, symbol: str):
        """
        replicates lists of 18 fields returned by binance
        """

        resp_dict = \
            {
                "symbol": symbol,
                "orderId": 1,
                "orderListId": -1,
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
                "time": 1000000000000,
                "updateTime": 1000000000000,
                "isWorking": "true",
                "origQuoteOrderQty": "0.000000"
            }

        return [resp_dict for _ in range(size)]


def mockinit(self):
    self.exchangeAPI = BinanceAPIMock()


def get_currency_pair_list(self) -> CurrencyList:
    return ['BTCUSD', 'BTCEUR', 'ETHBTC', 'ETHUSD', 'USDEUR']


@pytest.fixture
def date_2021_str():
    return '2021/01/01'


@pytest.fixture
def date_2021_10_str():
    return '2021/01/01 10:00'


def test_get_currency_list():
    cl = BinanceAPI().get_currency_list()
    print(cl)
    assert isinstance(cl, list)


def test_get_currency_list():
    dp = BinanceAPI().get_currency_pair_list()
    print(dp)
    assert isinstance(dp, list)


def test_get_historical_klines(date_2021_str, date_2021_10_str):
    kl = BinanceAPI().get_historical_klines(
        'BTCUSDT', date_2021_str, date_2021_10_str
    )
    assert isinstance(kl, list)
    assert isinstance(kl[0], list)
    for i in kl:
        assert len(i) == 12


def test_get_orders_wo_limit(monkeypatch):
    monkeypatch.setattr(BinanceAPI, 'init_exchange', mockinit)
    resp = BinanceAPI().get_orders_wo_limit(
        crypto_pair='BTCUSDT',
        limit=10
    )

    assert len(resp) == 11


def test__spot_download(monkeypatch, date_2021_str, date_2021_10_str):
    monkeypatch.setattr(BinanceAPI, 'init_exchange', mockinit)
    monkeypatch.setattr(
        BinanceAPI, 'get_currency_pair_list', get_currency_pair_list)
    resp = BinanceAPI()._spot_download(
        crypto_list=['BTC', 'ETH'],
        start_time=date_2021_str,
        end_time=date_2021_10_str,
        limit=10
    )
    assert len(resp) == 4
    for vals in resp.values():
        assert len(vals) == 11


def test_get_spot_trades(monkeypatch):
    monkeypatch.setattr(BinanceAPI, 'init_exchange', mockinit)
    monkeypatch.setattr(
        BinanceAPI, 'get_currency_pair_list', get_currency_pair_list)
    API_KEY, SECRET_KEY = '', ''
    resp = BinanceAPI(API_KEY, SECRET_KEY).get_spot_trades(limit=10)
    assert len(resp) == 5
    for vals in resp.values():
        assert len(vals) == 11
