import csv
import re
import sys


def valid_uid(uid):
    """Check if string matches DHIS2 UID pattern"""
    return re.compile("[A-Za-z][A-Za-z0-9]{10}").match(uid)


def write_csv(data, filename, header_row):
    """Write CSV data for both Python2 and Python3"""
    kwargs = {'newline': ''}
    mode = 'w'
    if sys.version_info < (3, 0):
        kwargs.pop('newline', None)
        mode = 'wb'

    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=str(','))
        writer.writerow(header_row)
        writer.writerows(data)
