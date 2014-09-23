from dateutil.parser import parse

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


def is_a_str(value, key):
    return True


"""Geospatial checks. Looks for coordinates, coordinate pairs, address strings, 
geo text (like country, state, city), zip codes, etc etc. Basically anything 
you might want to geocode or treat as a point. """

def is_a_coord(value, key=None, pos=None):
    if key:
        key = str(key).lower().strip()

    if key and key in ['latitude', 'longitude'] and is_a_int(value):
        return True

    if not is_a_int(value, key=key) or not is_a_float(value, key=key):
        return False

    if not len(str(value)) < 15:
        return False

    if not abs(float(value)) <= 180:
        return False

    # so we know we have a value that is between -180 and 180
    key_names = ['lat', 'lon', 'lng', 'coords', 'coordinates']
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


def is_geo_text(value, key=None, pos=None):
    admin_areas = [
        'city', 
        'state', 
        'country', 
        'zipcode',
        'county',
        'postal code',
        'adminArea1',
        'adminArea2',
        'adminArea3',
        'adminArea4',
        'adminArea5'
    ]

    if key and str(key).lower().strip() in admin_areas and value != '':
        return True

    # if most values are in list of cities
    # if most values are in list of countries
    # if key is ST and all values are two characters
    # if key is zip and all values have 4-9 digits
    return False
