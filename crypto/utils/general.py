from typing import Any


def retry_wrapper(attempts: int, check_value: Any, meet_criteria: bool=True):
    """
    Will retry function until expected output is returned (if meet_criteria is True)
    Will retry function until expected output is not returned (if meet_criteria is False)
    Or exceeds max number of attempts
    """
    def retry_fn(fn):
        def wrapper(*args):
            for i in range(attempts):
                fn_output = fn(*args)
                if meet_criteria:
                    if fn_output==check_value:
                        break
                else:
                    if fn_output!=check_value:
                        break
            return fn_output
        return wrapper
    return retry_fn
