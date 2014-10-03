Penny
========

### Inspect your data. Find the truth.

![alt tag](http://www.martianwatches.com/wp-content/uploads/2013/10/InspectorGadget.jpg)

Uncle Gadget was great and all, but when it came to real detective work, we all know Penny did the heavy lifting. Hence, Penny, the Python module that inspects stuff. Feed it rows or columns from a dataset, and get information about the column types -- including whether or not a given column represents a category or date. Penny also finds column headers (waaaay more reliably than the `Sniffer` class in to the standard `csv` module).

### Why?

If you're working with a few datasets, it's easy to figure out which columns are supposed to be dates, integers and even categories just by looking at the raw csv files. But if you need to programmatically deal with lots of datasets, this gets tedious fast. 

### Setup

Grab the package.

```
pip install penny
```

Or grab the code from GitHub.

```
git clone https://github.com/gati/penny
cd penny
pip install -r requirements.txt
```

### Getting Started

Guess the headers of a csv file.

```python
from penny.headers import get_headers

with open('your-awesome-file.csv') as csvfile:
    has_header, headers = get_headers(csvfile)
    
    # Prints True/False depending on whether or not headers were found
    print has_header 

    # Prints column headers or placeholders if real headers weren't found
    print headers # ['Example Header A', 'Example Header B']
```

Guess the data type of a column in your dataset.

```python    
from penny.inspectors import column_types_probabilities

fileobj = open('your-awesome-file.csv')
rows = list(csv.reader(fileobj))

# Get the values from column 0
column_0 = [x[0] for x in rows]
probs = column_types_probabilities(column_0)

# Prints something like {'date': 1, 'int': .75, 'category': 0 ...}
print probs
```

Or get type guesses for all the rows in your dataset at once.

```python    
from penny.inspectors import rows_types_probabilities

fileobj = open('your-awesome-file.csv')
rows = list(csv.reader(fileobj))
probs = rows_types_probabilities(rows)
```

Penny checks for a lot of data "types," not just the standard `int`, `str`, etc.
Here's the list (for now):

- **date** something `dateutil.parser` can parse into a `datetime` object 
- **int** a whole number 
- **bool** y/n or yes/no or something true/falsey 
- **float** a number with a decimal
- **category** something you might want to group records by
- **text** string longer than 90 characters (something you could get names/places/sentiment/etc from) 
- **id** unique for each row
- **coord** a float that might be a latitude or longitude
- **coord_pair** string that looks like "coord,coord"
- **proportion** column where all values sum to 1 or 100
- **street** house number + street name
- **city** one of the world's 80,000 largest cities
- **region** smaller than a country, bigger than a city. state, province, etc
- **country** a country name on the [ISO 3166 list](http://en.wikipedia.org/wiki/ISO_3166-1#Current_codes)
- **phone** a phone number
- **email** an email address
- **url** web address with or without http:// (so http://google.com or google.com)
- **address** a full address you could geocode with a service like Google Maps

Last but not least, you can also inspect a column for a single type.

```python    
from penny.list_check import column_probability_for_type

fileobj = open('your-awesome-file.csv')
rows = list(csv.reader(fileobj))

# Get the values from column 0
column_0 = [x[0] for x in rows]
prob = column_probability_for_type(column_0, 'date')

# Prints something like 0.78
print prob
```

### Contributing & Credits

This is a work in progress, so pull request at will. Some of this work was inspired by [messytables](https://github.com/okfn/messytables), which looks great for xls files but wasn't quite what I needed. Thanks to [Chris Albon](http://twitter.com/chrisalbon) for putting together a [repo of useful test datasets](https://github.com/chrisalbon/Variable-Type-Identification-Test-Datasets). 

Questions, concerns, devoted fan mail to [@jonathonmorgan](http://twitter.com/jonathonmorgan) on Twitter.

