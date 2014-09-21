import unittest
import csv
from penny.inspectors import (rows_types_probabilities, row_simple_types,
    categories_from_list)
import os

class InspectorsTest(unittest.TestCase):
    def test_row_simple_types(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        fileobj = open(cur_dir + '/data/banklist.csv')

        reader = csv.reader(fileobj)
        row = reader.next()
        types = row_simple_types(row)
        
        # First row is headers, should all be strings
        assert types[1:] == types[:-1]

        row = reader.next()
        types = row_simple_types(row)
        assert types == ['str', 'str', 'str', 'int', 'str', 'date', 'date']


    def test_rows_types_probabilties(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        fileobj = open(cur_dir + '/data/banklist.csv')

        rows = list(csv.reader(fileobj))
        probs = rows_types_probabilities(rows)
        
        assert probs[2]['category'] >= 0.9
        assert probs[3]['int'] >= 0.9
        assert probs[5]['date'] >= 0.9
        assert probs[6]['date'] >= 0.9

        fileobj = open(cur_dir + '/data/test_csv.csv')

        rows = list(csv.reader(fileobj))
        probs = rows_types_probabilities(rows)

        assert probs[2]['int'] > .9
        assert probs[3]['category'] > .9

        fileobj = open(cur_dir + '/data/EGViolatorsFinal.csv','rU')

        rows = list(csv.reader(fileobj))
        probs = rows_types_probabilities(rows)

        assert probs[1]['date'] > .9


    def test_categories_from_list(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        fileobj = open(cur_dir + '/data/banklist.csv')

        rows = list(csv.reader(fileobj))
        cats = categories_from_list(map(lambda x: x[2], rows))

        for st in ['FL', 'CA', 'IL', 'GA']:
            assert st in cats

def main():
    unittest.main()

if __name__ == "__main__":
    main()