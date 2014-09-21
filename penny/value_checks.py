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

        keyl = key.lower()
        if 'date' in keyl or 'time' in keyl:
            return True
        else:
            return False

    return True


def is_a_float(value, key=None):
    try:
        if "." in str(value):
            return float(value)

        return False
    except:
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
