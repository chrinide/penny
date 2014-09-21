import unittest
import csv
from penny.value_checks import *
import os

class ValueChecksTest(unittest.TestCase):
    def test_is_a_bool(self):
        pass

    def test_is_a_int(self):
        assert not is_a_int("50.15")
        assert not is_a_int(50.15)
        assert is_a_int("120938123")
        assert is_a_int(9283948324)

    def test_is_a_float(self):
        assert is_a_float("50.15")
        assert not is_a_float(100)

    def test_is_a_date(self):
        assert not is_a_date('ST')
        assert is_a_date('31-May-13')
        

def main():
    unittest.main()

if __name__ == "__main__":
    main()