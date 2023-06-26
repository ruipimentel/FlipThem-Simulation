import pytest

from util.bitstring import *

def test_read_bitstring():
    assert read_bitstring([0]) == 0
    assert read_bitstring([1]) == 1
    assert read_bitstring([0], 10.00, 11.25) == 10.00
    assert read_bitstring([1], 10.00, 11.25) == 11.25

    assert read_bitstring([0, 0]) == 0
    assert read_bitstring([0, 1]) == 1
    assert read_bitstring([1, 1]) == 2
    assert read_bitstring([1, 0]) == 3
    assert read_bitstring([0, 0], 10.00, 13.75) == 10.00
    assert read_bitstring([0, 1], 10.00, 13.75) == 11.25
    assert read_bitstring([1, 1], 10.00, 13.75) == 12.50
    assert read_bitstring([1, 0], 10.00, 13.75) == 13.75

    assert read_bitstring([0, 0, 0]) == 0
    assert read_bitstring([0, 0, 1]) == 1
    assert read_bitstring([0, 1, 1]) == 2
    assert read_bitstring([0, 1, 0]) == 3
    assert read_bitstring([1, 1, 0]) == 4
    assert read_bitstring([1, 1, 1]) == 5
    assert read_bitstring([1, 0, 1]) == 6
    assert read_bitstring([1, 0, 0]) == 7
    assert read_bitstring([0, 0, 0], 10.00, 18.75) == 10.00
    assert read_bitstring([0, 0, 1], 10.00, 18.75) == 11.25
    assert read_bitstring([0, 1, 1], 10.00, 18.75) == 12.50
    assert read_bitstring([0, 1, 0], 10.00, 18.75) == 13.75
    assert read_bitstring([1, 1, 0], 10.00, 18.75) == 15.00
    assert read_bitstring([1, 1, 1], 10.00, 18.75) == 16.25
    assert read_bitstring([1, 0, 1], 10.00, 18.75) == 17.50
    assert read_bitstring([1, 0, 0], 10.00, 18.75) == 18.75
