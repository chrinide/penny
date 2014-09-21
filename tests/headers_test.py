import unittest
import csv
from penny.headers import get_headers
import os

class HeadersTest(unittest.TestCase):
    def test_get_headers(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        file_name_headers = [
            ['test_csv.csv', 'permalink'],
            ['banklist.csv', 'Bank Name'],
            ['DJI.csv', 'Date'],
            ['travelers.gw001.csv', 'column_0'],
            ['daily.csv', 'column_0'],
            ['crisisnet (4).csv', 'id'],
            ['demodata.csv', 'clientid'],
            ['syria-incidents.csv', 'cityID'],
            ['nosdra_2014-07-07_10_25_35UTC_filtered.csv', 'id'],
            ['channing.csv', '']
        ]

        for fnh in file_name_headers:
            with open(cur_dir + '/data/' + fnh[0]) as csvfile:
                has_header, headers = get_headers(csvfile)
                print fnh[1], headers[0]
                assert headers[0] == fnh[1]

def main():
    unittest.main()

if __name__ == "__main__":
    main()