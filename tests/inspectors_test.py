import unittest
import csv
from penny.inspectors import (rows_types_probabilities, row_simple_types,
    categories_from_list, column_types_probabilities, 
    address_parts_probabilities)
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


    def test_column_types_probabilities(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        fileobj = open(cur_dir + '/data/banklist.csv')

        rows = list(csv.reader(fileobj))
        column = [x[2] for x in rows]

        p = column_types_probabilities(column, ['region'])

        assert 'region' in p
        assert p['region'] == 1

    
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
        assert probs[8]['region'] > .9


    def test_address_parts_probabilities(self):
        addresses = [
            '123 Main St',
            '456 Other St, Austin',
            '555 Other St, Austin, TX',
            '999 Another St, Austin, TX',
            '888 Another St, Austin, TX',
            '456788 Random Rd, Austin, TX'
        ]

        probs = address_parts_probabilities(addresses)

        assert probs['city'] > .5
        assert probs['state'] > .5
        assert probs['zip'] == 0

        addresses = [
            'I am the very model of a modern major general',
            'That is, like, so cool, with lots of commas and shit',
            'And then! We dance',
            '123 is my favorite sequence',
            '999',
            '95.456',
            'TX',
            'Ecuador',
            'Austin, TX',
            'Franklin, TX'
        ]

        probs = address_parts_probabilities(addresses)

        assert probs['city'] < .5
        assert probs['state'] < .5
        assert probs['zip'] < .5


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