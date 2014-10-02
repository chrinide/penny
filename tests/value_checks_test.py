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
        assert not is_a_date('-1479.2')
        assert not is_a_date('78.12345')

    def test_is_a_coord(self):
        assert not is_a_coord(190)
        assert not is_a_coord('hello!')
        assert is_a_coord("78.1")
        assert is_a_coord("-179.123")
        assert is_a_coord(170, key='lng')
        assert not is_a_coord(150)
        assert is_a_coord(32.8578872)

    def test_is_a_coord_pair(self):
        assert is_a_coord_pair("-37.123,148")
        assert is_a_coord_pair("180,89.1234")
        assert is_a_coord_pair("-37.123|148")
        assert is_a_coord_pair("180|89.1234")
        assert is_a_coord_pair("-37.123/148")
        assert is_a_coord_pair("180/89.1234")
        assert not is_a_coord_pair("180,91")
        assert not is_a_coord_pair("-181,-90")
        assert not is_a_coord_pair("-181.23,45")
        assert not is_a_coord_pair("91,91")

    def test_is_a_city(self):
        assert is_a_city('Cleveland')
        assert is_a_city('nairobi')
        assert is_a_city('LONDON')
        assert not is_a_city('France')

    def test_is_a_region(self):
        assert is_a_region('Ohio')
        assert is_a_region('Ontario')
        assert is_a_region('WA')
        assert is_a_region('montana')
        assert not is_a_region('murica')

    def test_is_a_country(self):
        assert is_a_country('United States')
        assert is_a_country('France')
        assert is_a_country('GERMANY')
        assert not is_a_country('murica')

    def test_is_a_address(self):
        assert is_a_address("123 Main Street")
        assert is_a_address("100 Congress Ave, Austin, 78701")
        assert is_a_address("Leister Square, London, UK")
        assert not is_a_address("Four score and seven years ago, blah blah")
        assert not is_a_address("125")
        assert not is_a_address("$99")

    def test_is_a_zip(self):
        assert is_a_zip("12345")
        assert is_a_zip("90210")
        assert is_a_zip("12345-9999")
        assert not is_a_zip("00010")
        assert not is_a_zip("100")
        assert not is_a_zip("00499")


    def is_a_text(self):
        assert is_a_text('I am the very model of a modern major general, I have information vegetable animal and mineral.')
        assert not is_a_text('100 Congress Ave, Austin Texas 78745 United States')


def main():
    unittest.main()

if __name__ == "__main__":
    main()