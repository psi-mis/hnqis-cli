#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time

from __init__ import *
from src.attribute_setter import create_or_update_attributevalues

USER_MESSAGE_UID = 'ct3X8eB5gRj'


def parse_args():
    usage = "hnqis-user-message [-s] [-u] [-p] -c -t -a" \
            "\n\n\033[1mExample:\033[0m " \
            "\nhnqis-user-message -s=data.psi-mis.org -u=admin -p=district -c=/path/to/file.csv" \
            "\n\n\033[1mCSV file structure:\033[0m         " \
            "\nusername | message                          " \
            "\n---------|--------                          " \
            "\nadmin    | Hi Admin!                        " \
            "\n                                            "
    parser = argparse.ArgumentParser(
        description="Post Message (User Attribute Value) sourced from CSV file", usage=usage)
    parser.add_argument('-s', dest='server', action='store',
                        help="DHIS2 server URL without /api/ e.g. -s=play.dhis2.org/demo")
    parser.add_argument('-c', dest='source_csv', action='store', help="CSV file with Messages",
                        required=True)
    parser.add_argument('-u', dest='username', action='store', help="DHIS2 username")
    parser.add_argument('-p', dest='password', action='store', help="DHIS2 password")
    parser.add_argument('-d', dest='debug', action='store_true', default=False, required=False,
                        help="Writes more info in log file")

    return parser.parse_args()


def validate_csv(data):
    if not data[0].get('username', None) or not data[0].get('message', None):
        raise CsvException("CSV not valid: CSV must have 'username' and 'message' as headers")

    object_uids = [obj['username'] for obj in data]
    if len(object_uids) != len(set(object_uids)):
        raise CsvException("Duplicate Objects (rows) found in the CSV")
    return True


def main():
    args = parse_args()
    init_logger(args.debug)
    log_start_info(__file__)

    api = Dhis(server=args.server, username=args.username, password=args.password)

    if '.psi-mis.org' not in args.server:
        log_info("This script is intended only for *.psi-mis.org")
        sys.exit()

    data = load_csv(args.source_csv)
    validate_csv(data)

    attr_get = {'fields': 'id,name,userAttribute'}
    attr = api.get('attributes/{}'.format(USER_MESSAGE_UID), params=attr_get)
    if attr['userAttribute'] is False:
        log_info("Attribute {} is not assigned to Users".format(USER_MESSAGE_UID))

    print(u"[{}] - Adding messages for \033[1m{}\033[0m \033[1musers\033[0m...".format(args.server, len(data)))
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\033[1m{}\033[0m".format("Aborted!"))
        pass

    for i, obj in enumerate(data, 1):
        # Look up user UID
        username = obj.get('username')
        params_user = {
            'fields': 'id,name',
            'filter': 'userCredentials.userInfo.userCredentials.username:eq:{}'.format(username)
        }
        lookup = api.get('users', params=params_user)
        user_uid = lookup['users'][0]['id']

        attribute_value = obj.get('message')
        params_get = {'fields': ':owner,userGroups'}
        user = api.get('users/{}'.format(user_uid), params=params_get)
        user_updated = create_or_update_attributevalues(obj=user, attribute_uid=USER_MESSAGE_UID,
                                                        attribute_value=attribute_value)
        api.put('users/{}'.format(user_uid), params=None, payload=user_updated)
        print(u"{}/{} - Added message for username \033[1m{}\033[0m".format(i, len(data), username))


if __name__ == "__main__":
    main()
