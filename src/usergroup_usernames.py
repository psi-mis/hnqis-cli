#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from __init__ import *

USER_MESSAGE_UID = 'ct3X8eB5gRj'


def parse_args():
    usage = "hnqis-usergroup-usernames [-s] [-u] [-p] -g" \
            "\n\n\033[1mExample:\033[0m " \
            "\nhnqis-usergroup-usernames -s=data.psi-mis.org -u=admin -p=district -g=aBcD2eF8j9h"
    parser = argparse.ArgumentParser(description="Get usernames of userGroup", usage=usage)
    parser.add_argument('-s', dest='server', action='store', help="DHIS2 server URL without /api/ e.g. -s=play.dhis2.org/demo")
    parser.add_argument('-g', dest='usergroup', action='store', help="userGroup UID", required=True)
    parser.add_argument('-u', dest='username', action='store', help="DHIS2 username")
    parser.add_argument('-p', dest='password', action='store', help="DHIS2 password")
    parser.add_argument('-d', dest='debug', action='store_true', default=False, required=False, help="Writes more info in log file")

    return parser.parse_args()


def main():
    args = parse_args()
    #init_logger(args.debug)
    #log_start_info(__file__)

    api = Dhis(server=args.server, username=args.username, password=args.password)

    if not valid_uid(args.usergroup):
        log_info("{} is not a valid UID".format(args.usergroup))
        sys.exit()

    params = {
        'fields': 'id,name, users[id, name, userCredentials[userInfo[userCredentials[username]]]]',
        'paging': False
    }
    data = api.get('userGroups/{}'.format(args.usergroup), params=params)

    file_name = 'usergroup_{}_users.csv'.format(args.usergroup)

    with open(file_name, 'wb') as csvfile:
        fieldnames = ['username', 'message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, encoding='utf-8', delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for u in data['users']:
            export = {
                'username': u['userCredentials']['userInfo']['userCredentials']['username']
            }
            writer.writerow(export)
        log_info("File exported to \033[1m{}\033[0m containing \033[1m{}\033[0m users for userGroup \033[1m{}\033[0m".format(file_name, len(data['users']), args.usergroup))


if __name__ == '__main__':
    main()
