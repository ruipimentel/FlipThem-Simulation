from typing import List, Literal

import random

import graycode

def random_bitstring(string_size: int) -> List[Literal[0, 1]]:
    return [ random.randint(0, 1) for _ in range(string_size) ]

def read_bitstring(bitstring: List[Literal[0, 1]], min_value=None, max_value=None) -> int | float:
    """
    Reads the contents of the specified bitstring as an integer (if `min_value` and
    `max_value` are not specified), or as a float (if values are supplied for both
    `min_value` and `max_value`).

    The way it reads the integer is through Gray Code.

    The way it computes the float value is by mapping the lowest Gray Code to
    `min_value`, the greatest to `max_value`, and the others proportionately.
    """

    integer_value = int(''.join([str(b) for b in bitstring]), 2)
    integer_value = graycode.gray_code_to_tc(integer_value)
    if min_value is not None and max_value is not None:
        return min_value + (max_value - min_value)*integer_value/(2**len(bitstring) - 1)
    return integer_value