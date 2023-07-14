import pytest

from util.bitstring import *

def test_read_bitstring():
    assert read_bitstring([0]) == 0
    assert read_bitstring([1]) == 1
    assert read_bitstring([0], as_graycode=True) == 0
    assert read_bitstring([1], as_graycode=True) == 1

    assert read_bitstring([0], 10.00, 11.25) == 10.00
    assert read_bitstring([1], 10.00, 11.25) == 11.25
    assert read_bitstring([0], 10.00, 11.25, as_graycode=True) == 10.00
    assert read_bitstring([1], 10.00, 11.25, as_graycode=True) == 11.25

    assert read_bitstring([0, 0]) == 0
    assert read_bitstring([0, 1]) == 1
    assert read_bitstring([1, 0]) == 2
    assert read_bitstring([1, 1]) == 3
    assert read_bitstring([0, 0], as_graycode=True) == 0
    assert read_bitstring([0, 1], as_graycode=True) == 1
    assert read_bitstring([1, 1], as_graycode=True) == 2
    assert read_bitstring([1, 0], as_graycode=True) == 3

    assert read_bitstring([0, 0], 10.00, 13.75) == 10.00
    assert read_bitstring([0, 1], 10.00, 13.75) == 11.25
    assert read_bitstring([1, 0], 10.00, 13.75) == 12.50
    assert read_bitstring([1, 1], 10.00, 13.75) == 13.75
    assert read_bitstring([0, 0], 10.00, 13.75, as_graycode=True) == 10.00
    assert read_bitstring([0, 1], 10.00, 13.75, as_graycode=True) == 11.25
    assert read_bitstring([1, 1], 10.00, 13.75, as_graycode=True) == 12.50
    assert read_bitstring([1, 0], 10.00, 13.75, as_graycode=True) == 13.75

    assert read_bitstring([0, 0, 0]) == 0
    assert read_bitstring([0, 0, 1]) == 1
    assert read_bitstring([0, 1, 0]) == 2
    assert read_bitstring([0, 1, 1]) == 3
    assert read_bitstring([1, 0, 0]) == 4
    assert read_bitstring([1, 0, 1]) == 5
    assert read_bitstring([1, 1, 0]) == 6
    assert read_bitstring([1, 1, 1]) == 7
    assert read_bitstring([0, 0, 0], as_graycode=True) == 0
    assert read_bitstring([0, 0, 1], as_graycode=True) == 1
    assert read_bitstring([0, 1, 1], as_graycode=True) == 2
    assert read_bitstring([0, 1, 0], as_graycode=True) == 3
    assert read_bitstring([1, 1, 0], as_graycode=True) == 4
    assert read_bitstring([1, 1, 1], as_graycode=True) == 5
    assert read_bitstring([1, 0, 1], as_graycode=True) == 6
    assert read_bitstring([1, 0, 0], as_graycode=True) == 7

    assert read_bitstring([0, 0, 0], 10.00, 18.75) == 10.00
    assert read_bitstring([0, 0, 1], 10.00, 18.75) == 11.25
    assert read_bitstring([0, 1, 0], 10.00, 18.75) == 12.50
    assert read_bitstring([0, 1, 1], 10.00, 18.75) == 13.75
    assert read_bitstring([1, 0, 0], 10.00, 18.75) == 15.00
    assert read_bitstring([1, 0, 1], 10.00, 18.75) == 16.25
    assert read_bitstring([1, 1, 0], 10.00, 18.75) == 17.50
    assert read_bitstring([1, 1, 1], 10.00, 18.75) == 18.75
    assert read_bitstring([0, 0, 0], 10.00, 18.75, as_graycode=True) == 10.00
    assert read_bitstring([0, 0, 1], 10.00, 18.75, as_graycode=True) == 11.25
    assert read_bitstring([0, 1, 1], 10.00, 18.75, as_graycode=True) == 12.50
    assert read_bitstring([0, 1, 0], 10.00, 18.75, as_graycode=True) == 13.75
    assert read_bitstring([1, 1, 0], 10.00, 18.75, as_graycode=True) == 15.00
    assert read_bitstring([1, 1, 1], 10.00, 18.75, as_graycode=True) == 16.25
    assert read_bitstring([1, 0, 1], 10.00, 18.75, as_graycode=True) == 17.50
    assert read_bitstring([1, 0, 0], 10.00, 18.75, as_graycode=True) == 18.75
