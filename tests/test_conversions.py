import pytest
from crypto.binance_api import BinanceAPI
from crypto.conversion import Conversion

def test_conversion_split_pair(): 
    out = Conversion(BinanceAPI).split_pair('BUSDUSDT')
    assert isinstance(out, dict) 

def test_conversion_get_currencies_to_convert(): 
    converter = Conversion(BinanceAPI)
    out1 = converter.get_currencies_to_convert(
        ['EURBUSD', 'BTCUSDT', 'BUSDUSDT']
    )
    assert isinstance(out1, dict) 

    out2 = converter.get_currencies_to_convert(
        BinanceAPI().get_currency_pair_list()
    )
    assert isinstance(out2, dict)

def test_conversion_find_conversion_pair(): 
    converter = Conversion(BinanceAPI)
    current_pair = ('BTC', 'BUSD')
    target_currency = 'USDT'

    new_pair = converter.find_conversion_pair(current_pair, target_currency)
    assert isinstance(new_pair, str)
    assert target_currency in new_pair

def test_conversion_add_conversion_pair(): 
    converter = Conversion(BinanceAPI)
    current_pair_dict = {'BTCBUSD': [('BTC', 'BUSD')], 'EURBUSD': [('EUR', 'BUSD')]}
    target_currency = 'USDT'

    new_pair_dct = converter.add_conversion_pair(current_pair_dict, target_currency)
    assert isinstance(new_pair_dct, dict)
    for val in new_pair_dct.values():
        assert target_currency in val[1]

def test_create_currency_conversion_dict():
    converter = Conversion(BinanceAPI)
    currency_data = ["BTCBUSD", "EURBUSD"]
    target_currency = 'USDT'
    conv_dict = converter.create_currency_conversion_dict(currency_data, target_currency)
    assert isinstance(conv_dict, dict)
