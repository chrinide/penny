import csv
from .inspectors import (row_simple_types, rows_types_probabilities, 
    categories_from_list)

"""Takes a file object and finds the column headers (if they exist). 

:param fileobj: a file object
:returns found, list of headers
:rtype bool, list
"""
def get_headers(fileobj):
    sniffer = csv.Sniffer()
    sample_contents = fileobj.read(1024)
    dialect = sniffer.sniff(sample_contents)
    fileobj.seek(0)
    reader = csv.reader((line.lstrip() for line in fileobj), dialect=dialect)

    # the csv module sniffer is pretty conversative, so if it thinks we have 
    # a header, let's assume that we do
    if sniffer.has_header(sample_contents):
        return True, reader.next()
    
    # otherwise let's do our own investigation
    rows = list(reader)
    pos_header = rows[0]
    pos_header_types = row_simple_types(pos_header)

    # First make sure each column is a string (headers are always strings)
    if pos_header_types[0] == 'str' and pos_header_types[1:] == pos_header_types[:-1]:
        # now get types for each column
        probs = rows_types_probabilities(rows[1:])
        for i, p in enumerate(probs):
            for k,v in p.iteritems():
                # if the column isn't a string, then its type is different
                # from the first column, so we can assume the first column 
                # is a header
                if v > .5 and k != 'str':
                    # if the column is a category, it might also be 
                    # labeled a string, in which case we should make sure 
                    # the header is not found in the list of categories 
                    # pulled from this dataset
                    if k != 'category':
                        return True, pos_header

                    column_values = map(lambda x: x[i], rows[:1])
                    cats = categories_from_list(column_values)
                    if pos_header[i] not in cats:
                        return True, pos_header 

    # worst case scenario, make up some column names
    return False, ['column_%s' % str(n) for n in range(len(rows[0]))]
