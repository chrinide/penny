import itertools
import math
import collections
from .value_checks import (is_a_date, is_a_int, is_a_bool, is_a_float,
    is_a_coord, is_a_coord_pair, is_a_country, is_a_city, is_a_region,
    is_a_address, is_a_text, is_a_zip, is_a_street, is_a_phone, is_a_url, 
    is_a_email)


"""Guesses likelikhood that a column is of the requested type based on its
values.

:param values: a list of values (probably a column in a csv)
:param for_type: string name of the desired type
:param pos: column position, optionally used for some types
:param key: string name of column header, optionally for some types
:returns probability that this column is of for_type
:rtype float
"""
def column_probability_for_type(values, for_type, pos=None, key=None):
    if for_type == 'category':
        return category_probability(values, key=key, pos=pos)
    elif for_type == 'id':
        return id_probability(values, key=key, pos=pos)
    elif for_type == 'proportion':
        return proportion_probability(values, key=key)

    type_checkers = {
        'date': is_a_date,
        'bool': is_a_bool,
        'int': is_a_int,
        'float': is_a_float,
        'coord': is_a_coord,
        'coord_pair': is_a_coord_pair,
        'street': is_a_street,
        'city': is_a_city,
        'region': is_a_region,
        'zipcode': is_a_zip,
        'phone': is_a_phone,
        'url': is_a_url,
        'email': is_a_email,
        'country': is_a_country,
        'address': is_a_address,
        'text': is_a_text
    }

    is_type = 0
    for value in values:
        if type_checkers[for_type](value):
            is_type += 1


    non_empty = [v for v in values if v != '']
    divisor = len(non_empty) if len(non_empty) > 0 else 1

    return float(is_type) / divisor


"""The likelihood that a given list of values is a unique id

:param values: a list of values to check
:param key: the column header (optional)
:param pos: the column position (optiona - eg 0 for the first column)
"""
def id_probability(values, key=None, pos=None):
    prob = 0

    if len(values) == len(set(values)):
        prob += 0.25
    else:
        # if val in all rows isn't unique, then it's not an id
        return 0

    if key and str(key).lower() == 'id':
        prob += 0.5

    if pos and pos == 0:
        prob += .25

    return prob

"""The likelihood that a given list of values is a proportion

:param values: a list of values to check
:param key: the column header (optional)
:param pos: the column position (optiona - eg 0 for the first column)
"""
def proportion_probability(values, key=None, pos=None):
    if column_probability_for_type(values, 'int') == 1:
        try:
            values = [int(v) for v in values]
        except:
            return 0
    elif column_probability_for_type(values, 'float') == 1:
        try:
            values = [float(v) for v in values]
        except:
            return 0
    else:
        return 0

    if sum(values) == 1 or sum(values) == 100:
        return 1

    return 0


"""The likelihood that a given list of values is a category. A category column
is assumed to have the following properties:

- most of its rows are not empty
- it's not populated with dates
- any given category label should be assigned to at least 2% of the rows
- 80% of the rows should be assigned to at least one category label, or...
- at least 10% of the rows must be assigned to one category label

It's not perfect, but it usually finds columns that you'd want to group as
categories when further analyzing a dataset.

:param values: a list of values to check
:param key: the column header (optional)
:param pos: the column position (optiona - eg 0 for the first column)
"""
def category_probability(values, key=None, pos=None):
    total_rows = len(values)
    non_empty = [r.strip() for r in values if r.strip() != '']

    # If this is a mostly empty rows, we don't want to use it
    if len(non_empty) < len(values) / 2:
        return 0

    # If this is a date field, we don't treat it as a category
    if column_probability_for_type(values, 'date', pos=pos, key=key) > .5:
        return 0

    # All category fields are 1 to many. If we detect a delimiter, split the
    # text field into a list. Otherwise treat the category as a list of 1
    delimiter = detect_delimiter(values)
    if delimiter:
        row_cats = [i.split(delimiter) for i in non_empty]
        all_cats = list(itertools.chain.from_iterable(row_cats))
    else:
        row_cats = [[x] for x in non_empty]
        all_cats = non_empty


    # at least 2% of the rows in the set must have any given value for it to
    # be considered a possible category
    threshold = int(.02 * len(non_empty))

    # number of categories
    matches = []
    failed_matches = []

    # This prodcues a list of two-item lists, like [String, Integer], where
    # String is the category label and Integer is the number of times that
    # value appears in the list
    for x,y in collections.Counter(all_cats).items():
        # y > 1 for small datasets (like 25 rows) where 1 row is more than
        # 2% of overall rows.
        if y > 1 and y > threshold:
            matches.append([x,y])
        else:
            failed_matches.append([x,y])

    if len(matches) == 0:
        return 0

    # Determine the number of rows that have been assigned to at least one
    # the values we determined to be a category using the 2% test above.
    total_categorized = 0
    total_uncategorized = 0

    all_matches = [x[0] for x in matches]
    for row_cat in row_cats:
        if len([x for x in row_cat if x in all_matches]) > 0:
            total_categorized += 1
        else:
            total_uncategorized += 1


    # If this is a bunch of numbers, it's probably not a category
    if all([is_a_int(v) or is_a_float(v) for v in values]) and \
            len(all_matches) > math.sqrt(total_rows) / 2:

        return 0 


    # If more than half the dataset isn't categorized based on this set of
    # labels, then it's probably not a category

    if float(total_uncategorized) / float(total_rows) >= .5:
        return 0

    # more than 20% of the rows aren't categorized, and none of the categories
    # are more than 10% of the dataset
    elif float(total_uncategorized) / float(total_rows) >= .2 and \
            all([float(x[1]) / float(len(non_empty)) < .1 for x in matches]):

        return 0
    else:
        tu = total_uncategorized if total_uncategorized > 0 else 1

        prob = float(total_categorized) / float(tu)
        uncategorized_ratio = float(tu) / float(total_categorized)

        print uncategorized_ratio
        if uncategorized_ratio > .5:
            return 0

        if prob >= 1:
            return 1

        return prob


"""Finds the delimeter used to separate values in a string. This is for
category columns in a dataset like a,b,c or a/b/c

:param values: list of values (probably a column from a csv)
:returns the delimiter or None
:rtype string or None
"""
def detect_delimiter(values):
    non_empty = [r for r in values if r != '']

    # If this is a mostly empty rows, we don't want to use it
    if len(non_empty) < len(values) / 2:
        return None

    delimiters = [',','|','/']

    # 50 is a wild guess, should be refined
    short_enough = [v for v in non_empty if len(v) < 50]
    if len(short_enough) < len(non_empty) / 2:
        return None

    # number of records with each type of delimiter
    delimeter_count = [0] * len(delimiters)
    for i,d in enumerate(delimiters):
        delimeter_count[i] = len([v for v in non_empty if d in v])

    # if more than half the records contain one type of delimeter, it wins
    possible_delimeters = []
    for i,dc in enumerate(delimeter_count):
        if dc > len(non_empty) / 2:
            possible_delimeters.append(delimiters[i])

    if len(possible_delimeters) != 1:
        return None

    delimiter = possible_delimeters[0]

    def average(s): return sum(s) * 1.0 / len(s)

    # get average word length and standard deviation
    categories = list(itertools.chain.from_iterable([i.split(delimiter) for i in non_empty]))
    word_lengths = [len(w) for w in categories]
    avg_word_length = average(word_lengths)
    variance = map(lambda x: (x - avg_word_length)**2, word_lengths)
    standard_deviation = math.sqrt(average(variance))

    # this was probably a text field that used commas (or whatever) as part
    # of sentences.
    if standard_deviation > 6:
        return None

    return delimiter