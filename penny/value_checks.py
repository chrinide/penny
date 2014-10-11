from dateutil.parser import parse
from geo_lookup import get_places_by_type
from address import AddressParser
from email.utils import parseaddr
import phonenumbers
import re

def is_a_bool(value, key=None):
    bool_words = ['y','yes','n','no','true','false','t','f','on','off']
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

    if is_a_zip(value, key=key):
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


def is_a_text(value, key=None):
    if not is_a_str(value, key=key):
        return False

    return len(str(value).strip()) > 90


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
    delimeters = [',','|','/']
    disallowed = "(){}[]"

    value = str(value).strip()
    possible_matches = [d for d in delimeters if d in value]
    
    # if more than one of these is present or none of them, than this isn't 
    # a pair
    if len(possible_matches) != 1:
        return False

    # Get rid of weird shit people put in coord pair columns
    value = value.translate(None, disallowed)

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

    non_addrs = ['|','/','?','!','@','$','%']
    if len([na for na in non_addrs if na in value]) > 0:
        return False

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

    if str(value).count('-') == 1 and len(str(value)) == 10:
        primary = str(value).split('-')[0]
    else:
        primary = value

    try:
        primary = int(primary)
    except:
        return False

    if len(str(primary)) == 5 and int(primary) > 499:
        return True

    return False


ap = AddressParser()
def address_pieces(value):
    if not is_a_str(value):
        return [], None

    value = str(value).strip()

    if len(value) > 80:
        return [], None

    address = ap.parse_address(value)

    keys = [
        'house_number', 
        'street', 
        'city',
        'zip',
        'state'
    ]

    return [key for key in keys if getattr(address, key, None)], address


"""Check if a string is a house number + street name. The street part of an 
address. Note that we return false if this is a more complete address. """
def is_a_street(value, key=None, pos=None):
    has,address = address_pieces(value)

    if len(has) == 2 and 'house_number' in has and 'street' in has:
        return not is_a_address(value)
    else:
        return False


"""Check to see if this is enough of an address that it could be geocoded. So 
has at least a city + state, or at least street + city"""
def is_a_address(value, key=None, pos=None):
    has,address = address_pieces(value)
    
    if len(has) >= 2:
        if getattr(address, 'city', None):
            return True
        
        pieces = value.split(' ')
        if len(pieces) > 2:
            """Sometimes we get an address like 100 Congress Austin TX, so let's 
            take a stab at breaking up the city/state in a way AddressParser 
            might understand"""
            pieces[len(pieces) - 2] = pieces[len(pieces) - 2] + ','

            has,address = address_pieces(' '.join(pieces))
            if len(has) > 2 and getattr(address, 'city', None):
                return True

    return False


def is_a_phone(value, key=None, pos=None):
    value = str(value).strip()

    if len(value) > 20:
        return False

    """Check for international numbers"""
    if value.startswith('+'):
        try:
            phonenumbers.parse(value)
            return True
        except:
            return False

    """Otherwise let's hope it's a US number"""
    reg = re.compile(".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?", re.S)
    matches = reg.search(value)

    """We're not looking for text fields that contain phone numbers, only fields 
    that are dedicated to phone number"""
    if matches and len(matches.group(1)) == len(value):
        return True


    return False


def is_a_email(value, key=None, pos=None):
    value = str(value).strip()

    possible = parseaddr(value)
    if possible[1] == '':
        return False
    
    e = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
    m = e.search(possible[1])
    if not m:
        return False

    if len(m.group(0)) == len(possible[1]):
        return True

    return False


def is_a_url(value, key=None, pos=None):
    # blatantly ripped from Django
    regex = re.compile(
        r'(^https?://)?'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    value = str(value).strip()
    m = regex.search(value)

    if not m:
        return False

    return len(m.group(0)) == len(value)
