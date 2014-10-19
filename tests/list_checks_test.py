import unittest
import csv
from penny.list_checks import *
import os

class ListChecksTest(unittest.TestCase):
    def test_id_probability(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        fileobj = open(cur_dir + '/data/swdata.csv')
        rows = list(csv.reader(fileobj))
        prob = id_probability(map(lambda x: x[0], rows[1:]))

        assert prob == 0

        fileobj = open(cur_dir + '/data/mps_tanzania.csv')
        rows = list(csv.reader(fileobj))
        prob = id_probability(map(lambda x: x[4], rows[1:]))

        assert prob == 0.25

        prob = id_probability(map(lambda x: x[4], rows[1:]), key='id')

        assert prob == 0.75


    def test_detect_delimiter(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        fileobj = open(cur_dir + '/data/listofdeath.csv')
        rows = list(csv.reader(fileobj))

        delim = detect_delimiter(map(lambda x: x[5], rows[1:]))
        assert delim == '/'

        delim = detect_delimiter(map(lambda x: x[4], rows[1:]))
        assert delim == None


    def test_column_probability_for_type(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        fileobj = open(cur_dir + '/data/chicago_homicides.csv')
        rows = list(csv.reader(fileobj))

        prob = column_probability_for_type(map(lambda x: x[19], rows[1:]), 
                    'coord', key='Latitude')

        prob2 = column_probability_for_type(map(lambda x: x[20], rows[1:]), 
                    'coord', key='Longitude')

        prob3 = column_probability_for_type(map(lambda x: x[21], rows[1:]), 
                    'coord_pair', key='Location')

        assert prob > .7
        assert prob2 > .7
        assert prob3 > .7


    def test_category_probability(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))

        def should_be_category(col_num, rows, dataset, should=True):
            prob = category_probability(map(lambda x: x[col_num], rows[1:]))
            print str(prob), str(should), str(col_num), dataset
            #if col_num == 9 and dataset == 'ak_bill_votes.csv':
            #    print map(lambda x: x[col_num], rows[1:])
            if should:
                assert prob >= .5
            else:
                assert prob < .5


        def check_cats(filename, yes=[], no=[]):
            fileobj = open(cur_dir + '/data/' + filename,'rU')
            rows = list(csv.reader(fileobj))
            for num in yes:
                should_be_category(num, rows, filename)

            for num in no:
                should_be_category(num, rows, filename, should=False)
        
        
        # banklist
        check_cats('banklist.csv', yes=[2], no=[0,1,3,4,5])
        
        # test_csv
        check_cats('test_csv.csv', yes=[3,5,8,9], no=[0,1,2,4,6,7])

        # channing
        check_cats('channing.csv', yes=[6,2], no=[0,1,3,4,5])

        # crisisnet
        check_cats('crisisnet (4).csv', yes=[2,8,11], no=[0,1,3,4,5,6,7,9,10])

        # nosdra_2014...
        check_cats('nosdra_2014-07-07_10_25_35UTC_filtered.csv', yes=[2,5,4], no=[0,1,3])
        
        # mps_tanzania
        check_cats('mps_tanzania.csv', yes=[1], no=[0,2,3,4,5,6,7,8,9])

        # listofdeath.csv
        check_cats('listofdeath.csv', yes=[5,1], no=[0,2,3,4,6,7,8,9,10,11])

        # EGViolatorsFinal.csv
        check_cats('EGViolatorsFinal.csv', yes=[0,3,4,5,6,7,8], no=[1,2,9])
        

def main():
    unittest.main()

if __name__ == "__main__":
    main()