# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2016 David Huser

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function

import json
import logging
import logging.handlers
import os
import re
import sys
from datetime import datetime

import unicodecsv as csv

import requests

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class CsvException(Exception):
    pass


def load_csv(path):
    try:
        with open(path, 'rb') as csvfile:
            # infer delimiter / dialect
            dialect = csv.Sniffer().sniff(csvfile.read(), delimiters=';,')
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)
            return [row for row in reader]
    except csv.Error as e:
        raise CsvException(e)


def get_pkg_version():
    __version__ = ''
    with open(os.path.join(ROOT_DIR, '__version__.py')) as f:
        exec (f.read())
    return __version__


def valid_uid(uid):
    """Check if string matches DHIS2 UID pattern"""
    return re.compile("[A-Za-z][A-Za-z0-9]{10}").match(uid)


def init_logger(debug_flag):
    logformat = '%(levelname)s:%(asctime)s %(message)s'
    datefmt = '%Y-%m-%d-%H:%M:%S'
    filename = 'hnqis-cli.log'
    debug_flag = debug_flag

    # only log 'requests' library's warning messages (including errors)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if debug_flag:
        logging.basicConfig(filename=filename, level=logging.DEBUG, format=logformat,
                            datefmt=datefmt)
    else:
        logging.basicConfig(filename=filename, level=logging.INFO, format=logformat,
                            datefmt=datefmt)


def log_start_info(script_path):
    script_name = os.path.splitext(os.path.basename(script_path))[0]
    logging.info(u"\n\n===== hnqis-cli v{} - {} =====".format(get_pkg_version(), script_name))


def log_info(text):
    if isinstance(text, Exception):
        logging.debug(repr(text))
    else:
        try:
            print(text)
        except UnicodeDecodeError:
            print(text.encode('utf-8'))
        finally:
            logging.info(text.encode('utf-8'))


def log_debug(text):
    logging.debug(text.encode('utf-8'))


class ConfigException(Exception):
    pass


class Config(object):
    def __init__(self, server, username, password):

        if not server:
            dish = self.get_dish()
            server = dish['baseurl']
            username = dish['username']
            password = dish['password']

        if '/api' in server:
            print('Please do not specify /api/ in the server url')
            sys.exit()
        if server.startswith('localhost') or server.startswith('127.0.0.1'):
            server = 'http://{}'.format(server)
        elif server.startswith('http://'):
            server = server
        elif not server.startswith('https://'):
            server = 'https://{}'.format(server)
        self.auth = (username, password)

        self.api_url = '{}/api'.format(server)
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.file_timestamp = '{}_{}'.format(now, server.replace('https://', '').replace('.', '-').replace('/', '-'))

    @staticmethod
    def get_dish():

        print("No Server URL given, searching for dish.json ...")

        fn = 'dish.json'
        dish_location = ''

        if 'DHIS_HOME' in os.environ:
            dish_location = os.path.join(os.environ['DHIS_HOME'], fn)
        else:
            home_path = os.path.expanduser(os.path.join("~"))
            for root, dirs, files in os.walk(home_path):
                if fn in files:
                    dish_location = os.path.join(root, fn)
                    break
        if not dish_location:
            raise ConfigException("dish.json not found - searches in $DHIS_HOME and in your home folder")

        with open(dish_location, 'r') as f:
            dish = json.load(f)
            valid = False
            try:
                valid = all([dish['dhis'], dish['dhis']['baseurl'], dish['dhis']['username'], dish['dhis']['password']])
            except KeyError:
                pass
            if not valid:
                raise ConfigException(
                    "dish.json found at {} but not configured according dish.json format "
                    "(see https://github.com/baosystems/dish#Configuration for details)".format(dish_location))

            return {'baseurl': dish['dhis']['baseurl'], 'username': dish['dhis']['username'],
                    'password': dish['dhis']['password']}


class Dhis(Config):
    public_access = {
        'none': '--------',
        'readonly': 'r-------',
        'readwrite': 'rw------'
    }

    def __init__(self, server, username, password):
        Config.__init__(self, server, username, password)

    def get(self, endpoint, file_type='json', params=None):
        url = '{}/{}.{}'.format(self.api_url, endpoint, file_type)

        log_debug(u"GET: {} - parameters: {}".format(url, json.dumps(params)))

        try:
            r = requests.get(url, params=params, auth=self.auth)
        except requests.RequestException as e:
            self.abort(e)

        else:
            log_debug(u"URL: {}".format(r.url))
            if r.status_code == 200:
                log_debug(u"RESPONSE: {}".format(r.text))
                if file_type == 'json':
                    return r.json()
                else:
                    return r.text
            else:
                self.abort(r)

    def post(self, endpoint, params, payload):
        url = '{}/{}'.format(self.api_url, endpoint)
        log_debug(u"POST: {} \n parameters: {} \n payload: {}".format(url, json.dumps(params), json.dumps(payload)))

        try:
            r = requests.post(url, params=params, json=payload, auth=self.auth)
        except requests.RequestException as e:
            self.abort(e)
        else:
            if r.status_code != 200:
                self.abort(r)

    def put(self, endpoint, params, payload):
        url = '{}/{}'.format(self.api_url, endpoint)
        log_debug(u"PUT: {} \n parameters: {} \n payload: {}".format(url, json.dumps(params), json.dumps(payload)))

        try:
            r = requests.put(url, params=params, json=payload, auth=self.auth)
        except requests.RequestException as e:
            self.abort(e)
        else:
            if r.status_code != 200:
                self.abort(r)

    def get_dhis_version(self):
        """ return DHIS2 verson (e.g. 26) as integer"""
        response = self.get(endpoint='system/info', file_type='json')

        # remove -snapshot for play.dhis2.org/dev
        snapshot = '-SNAPSHOT'
        version = response.get('version')
        if snapshot in version:
            version = version.replace(snapshot, '')

        return int(version.split('.')[1])

    @staticmethod
    def abort(e):
        msg = u"++++++ ERROR ++++++\nHTTP code: {}\nURL: {}\nRESPONSE:\n{}"
        log_info(msg.format(e.status_code, e.url, e.text))
        sys.exit()
