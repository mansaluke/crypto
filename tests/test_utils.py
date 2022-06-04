import pytest
from crypto.utils import *

retry_value = 0

def test_retry_wrapper():
    @retry_wrapper(attempts=5, check_value=10)
    def func():
        global retry_value
        retry_value = retry_value + 1
        return retry_value

    final_value = func()
    assert final_value == 5
