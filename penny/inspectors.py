from .value_checks import (is_a_date, is_a_int, is_a_bool, is_a_float, 
    is_a_coord, is_a_coord_pair, is_a_city)
from .list_checks import column_probability_for_type
import collections
from address import AddressParser

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
        else:
            try:
                int_col = int(col)
                types.append('int')
            except:
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
        'ordinal', 
        'id',
        'coord',
        'coord_pair',
        'street',
        'city',
        'region',
        'zipcode',
        'phone',
        'email',
        'url',
        'country',
        'address',
        'text',
        'proportion'
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



"""Determine if a column is an address that can be separated into city, state, 
and zipcode

:param values: a list of values
:param num_rows: max number of rows to test
:returns a dict with city, state and zip probabilities
"""
def address_parts_probabilities(values, num_rows=100):
    len_values = len(values)
    ap = AddressParser()
    has = { 'city': 0, 'state': 0, 'zip': 0 }
    probs = { 'city': 0, 'state': 0, 'zip': 0 }
    max_rows = num_rows if num_rows < len_values - 1 else len_values - 1 
        
    if not column_probability_for_type(values[:max_rows], 'address') > .5:
        return probs

    for v in values[:max_rows]:
        if ',' not in v:
            tokens = v.split(' ')
            for i,token in enumerate(tokens):
                if len(token) > 1 and is_a_city(token):
                    tokens[i] = token + ','
                    break

            v = ' '.join(tokens)

        addr = ap.parse_address(v)
        for k in has.keys():
            if getattr(addr, k, None):
                has[k] += 1

    for k in probs.keys():
        probs[k] = float(has[k]) / max_rows

    return probs



def categories_from_list(values):
    non_empty = [r for r in values if r != '']
    threshold = int(.05 * len(non_empty))
    return [x for x, y in collections.Counter(non_empty).items() if y > threshold]
