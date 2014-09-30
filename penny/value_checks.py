from dateutil.parser import parse
from geo_lookup import get_places_by_type
from address import AddressParser

def is_a_bool(value, key=None):
    bool_words = ['y,yes,n,no,true,false,t,f,on,off']
    return value.lower().strip() in bool_words


def is_a_date(value, key=None):
    """
    Dateutil recognizes some letter combinations as dates, which is almost 
    always something that isn't really a date (like a US state abbreviation)
    """
    if not any(char.isdigit() for char in value):
        return False

    try:
        pos_date = parse(value)
    except:
        return False

    """ 
    If we can also parse this as a straigtup integer it's probably not a 
    date. Unless of course the word date or time is in the column name, 
    then it might be a timestamp.
    """
    if is_a_int(value, key):
        if not key:
            return False

        keyl = str(key).lower()
        if 'date' in keyl or 'time' in keyl:
            return True
        else:
            return False

    if is_a_float(value, key):
        keyl = str(key).lower()
        if 'date' in keyl or 'time' in keyl:
            return True

        if float(value) < 0:
            return False

        """
        This is iffy. Obviously it's totally possible to have infinitely 
        precise measurements, but we're going to guess that if there are 
        more numbers to the right of the decimal point than the left, we 
        are probably dealing with a coordinate (or something)
        """
        pieces = str(value).split('.')
        if len(pieces[1]) > len(pieces[0]):
            return False

    return True


def is_a_float(value, key=None):
    if "." in str(value):
        try:
            v = float(value)
            return True
        except:
            return False

    return False


def is_a_int(value, key=None):
    if is_a_float(value):
        return False

    try:
        int(value)
        return True
    except:
        return False


def is_a_str(value, key=None):
    if not value or str(value).strip() == "":
        return False

    if is_a_date(value) or is_a_float(value) or is_a_int(value):
        return False

    return True


"""Geospatial checks. Looks for coordinates, coordinate pairs, address strings, 
geo text (like country, state, city), zip codes, etc etc. Basically anything 
you might want to geocode or treat as a point. """

def is_a_coord(value, key=None, pos=None):
    if key:
        key = str(key).lower().strip()

    if key and key in ['latitude', 'longitude'] and is_a_int(value):
        return True

    if not is_a_int(value, key=key) and not is_a_float(value, key=key):
        return False

    if not abs(float(value)) <= 180:
        return False

    # so we know we have a value that is between -180 and 180
    key_names = ['lat', 'lon', 'lng', 'long', 'coords', 'coordinates']
    if key and any([k in key for k in key_names]):
        return True

    return is_a_float(value, key=key)


def is_a_coord_pair(value, key=None, pos=None):
    delimeters = [',','|','/',' ']
    possible_matches = [d for d in delimeters if d in str(value).strip()]
    
    # if more than one of these is present or none of them, than this isn't 
    # a pair
    if len(possible_matches) != 1:
        return False

    delimiter = possible_matches[0]
    
    possible_cords = value.split(delimiter)
    if len(possible_cords) != 2:
        return False

    # All parts have to be floats or ints
    if not all([is_a_float(x) or is_a_int(x) for x in possible_cords]):
        return False

    # max abs lat is 90, max abs lng is 180
    if any([abs(float(x)) > 180 for x in possible_cords]):
        return False

    if all([abs(float(x)) > 90 for x in possible_cords]):
        return False

    """If one is a coord and the other is an int or float, let's use it"""
    if any([is_a_coord(x) for x in possible_cords]):
        return True

    return False
    

def is_a_place(value, place_type, key=None):
    if not is_a_str(value):
        return False

    value = str(value).strip()

    # If your country's name is longer than 40 characters, you're doing 
    # something wrong.
    if len(value) > 40:
        return False

    if key:
        key = str(key).lower().strip()

    if key and key in [place_type]:
        return True

    if len(get_places_by_type(value, place_type)) > 0:
        return True

    if place_type in ['region'] and len(value) < 4 and \
        len(get_places_by_type(value, place_type + '_iso_code')) > 0:
        return True

    return False


def is_a_city(value, key=None, pos=None):
    return is_a_place(value, 'city', key=key)


def is_a_region(value, key=None, pos=None):
    return is_a_place(value, 'region', key=key)


def is_a_country(value, key=None, pos=None):
    return is_a_place(value, 'country', key=key)


def is_a_zip(value, key=None, pos=None):
    if key:
        key = str(key).lower().strip()

    if key and key in ['zip', 'zipcode', 'postal code']:
        return True

    if '-' in str(value):
        if len(value) == 10:
            return True

        primary = str(value).split('-')[0]
    else:
        primary = value

    if not is_a_int(value):
        return False

    if len(str(value)) == 5 and int(value) > 499:
        return True

    return False


def is_a_address(value, key=None, pos=None):
    if not is_a_str(value):
        return False

    value = str(value).strip()

    if len(value) > 80:
        return False

    ap = AddressParser()
    address = ap.parse_address(value)

    keys = [
        'house_number', 
        'street', 
        'city',
        'zip',
        'state'
    ]

    has = [key for key in keys if getattr(address, key, None)]

    if len(has) >= 2:
        return True

    return False
