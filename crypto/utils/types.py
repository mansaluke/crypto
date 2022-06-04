from typing import List


Currency = str
Pair = str
Crypto = Currency
Fiat = Currency
Stable = Crypto
CurrencyList = List[Currency]
CryptoList = List[Crypto]
Pair = str
PairList =  List[Pair]


class Price(float):
    def __new__(cls, value: str | float | int) -> float:
        return super().__new__(cls, value)
