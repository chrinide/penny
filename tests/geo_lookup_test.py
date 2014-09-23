import unittest
import csv
from penny.geo_lookup import *
import os

class GeoLookupTest(unittest.TestCase):
    def test_is_a_city(self):
        assert len(get_places_by_type('Cleveland', 'city')) > 0
        assert len(get_places_by_type('cleveland', 'city')) > 0
        assert len(get_places_by_type('ohio', 'region')) > 0
        assert len(get_places_by_type('OH', 'region_iso_code')) > 0
        assert len(get_places_by_type('oh', 'region_iso_code')) > 0
        assert len(get_places_by_type('Missouri', 'country')) == 0


def main():
    unittest.main()

if __name__ == "__main__":
    main()