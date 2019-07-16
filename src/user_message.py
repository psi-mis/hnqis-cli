#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import time

from dhis2 import Api, setup_logger, logger, load_csv
from .attribute_setter import create_or_update_attributevalues

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
        raise ValueError("CSV not valid: CSV must have 'username' and 'message' as headers")

    object_uids = [obj['username'] for obj in data]

    duplicates = set([x for x in object_uids if object_uids.count(x) > 1])
    if duplicates:
        raise ValueError("Duplicate users found in the CSV: {}".format(', '.join(duplicates)))
    return True


def main():
    args = parse_args()
    setup_logger()
    api = Api(server=args.server, username=args.username, password=args.password)

    if '.psi-mis.org' not in args.server and '.hnqis.org' not in args.server:
        logger.warn("This script is intended only for *.psi-mis.org or *.hnqis.org")
        sys.exit()

    data = list(load_csv(args.source_csv))
    validate_csv(data)

    attr = api.get('attributes/{}'.format(USER_MESSAGE_UID), params={'fields': 'id,name,userAttribute'}).json()
    if attr['userAttribute'] is False:
        logger.error("Attribute {} is not assigned to Users".format(USER_MESSAGE_UID))

    logger.info("[{}] - Adding messages for {} users...".format(args.server, len(data)))
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        logger.error("Aborted!")
        pass

    for i, obj in enumerate(data, 1):
        # Look up user UID
        username = obj.get('username')
        params_user = {
            'fields': 'id,name',
            'filter': 'userCredentials.userInfo.userCredentials.username:eq:{}'.format(username)
        }
        lookup = api.get('users', params=params_user).json()
        try:
            user_uid = lookup['users'][0]['id']
        except IndexError:
            print(u"User with username {} could not be found. Skipping...".format(username))
            pass
        else:
            attribute_value = obj.get('message')
            params_get = {'fields': ':owner,userGroups'}
            user = api.get('users/{}'.format(user_uid), params=params_get).json()
            user_updated = create_or_update_attributevalues(obj=user, attribute_uid=USER_MESSAGE_UID,
                                                            attribute_value=attribute_value)
            try:
                api.put('users/{}'.format(user_uid), params=None, data=user_updated)
            except Exception as e:
                logger.error("failed: {} {}".format(user_uid, e))
                pass
            else:
                logger.info("{}/{} - Added message for username {}".format(i, len(data), username))


if __name__ == "__main__":
    main()
