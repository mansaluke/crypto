from typing import List, AnyStr
from .exchange import Exchange
import logging

logger = logging.getLogger("crypto").addHandler(logging.NullHandler())


class Client:

    def __init__(self,
                 exchange: Exchange,
                 API_KEY=None,
                 SECRET_KEY=None,
                 crypto_filter: List=None,
                 target_currency: AnyStr='USDT'
                 ) -> Exchange:

        args = [
            API_KEY,
            SECRET_KEY,
            crypto_filter,
            target_currency
        ]

        self.ex = exchange(*args)
