from .value_checks import (is_a_date, is_a_int, is_a_bool, is_a_float, 
    is_a_coord, is_a_coord_pair)
from .list_checks import column_probability_for_type
import collections

"""Takes a list of values and returns a type signature

:param row: a list of values, potentially of different types
:returns a list of types, like ['str', 'str', 'int', 'date']
"""
def row_simple_types(row):
    types = []
    for col in row:
        if is_a_date(col):
            types.append('date')
        elif is_a_float(col):
            types.append('float')
        elif is_a_int(col):
            types.append('int')
        else:
            types.append('str')

    return types


"""Inspect a column/list of data to determine what type of data it contains.

:param values: the list of values to inspect
:param types: (optional) list of types as strings, like ['date', 'int', 'bool']
:param pos: (optional) column position in the dataset, like 0 for the first col
:param key: (optional) column header
:returns a dictional of type probabilities, like {'date': 1, 'int': .75}
"""
def column_types_probabilities(values, types=[], pos=None, key=None):
    all_types = [
        'date', 
        'int', 
        'bool', 
        'float', 
        'category', 
        'id',
        'coord',
        'coord_pair',
        'city',
        'region',
        'country',
        'address'
    ]

    types_to_check = types or all_types
    types = {}
    for ttc in types_to_check:
        types[ttc] = column_probability_for_type(values, ttc, pos=pos, key=key)

    return types


"""Get the column_types_probabilities value for each row in a dataset

:param rows: the rows in your dataset
:param headers: a list of column headers (optional)
:param num_rows: max number of rows to use when inspecting types
:returns a list of type probabilities
"""
def rows_types_probabilities(rows, headers=[], num_rows=100):
    types = []
    rows = [row for row in rows if len(row) == len(rows[0])]
    max_rows = num_rows if num_rows < len(rows) else len(rows)

    for i in range(0,len(rows[0])):
        vals = map(lambda x: x[i], rows[:max_rows -1])

        kwargs = { 'pos': i }
        if headers:
            kwargs['key'] = headers[i]

        types.append(column_types_probabilities(vals, **kwargs))

    return types


def categories_from_list(values):
    non_empty = [r for r in values if r != '']
    threshold = int(.05 * len(non_empty))
    return [x for x, y in collections.Counter(non_empty).items() if y > threshold]
