#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import json
from datetime import datetime
import sys

from dhis2 import Api, setup_logger, logger

HEALTH_AREAS = [
    'CC',
    'CBRM',
    'DQI',
    'FP',
    'FP CFC',
    'FP SAM',
    'FP LPM',
    'HIV',
    'HT',
    'IMCI',
    'Mal',
    'MNH',
    'NBRes',
    'PAC',
    'STI',
    'TB',
    'VMMC',
    'VP',
    'WASH',
    'WEA',
]


def parse_args():
    usage = "hnqis-indicator-update [-s] [-u] [-p]" \
            "\n\n\033[1mExample:\033[0m " \
            "\nhnqis-indicator-update -s=data.psi-mis.org -u=admin -p=district"
    parser = argparse.ArgumentParser(
        description="Update integrated Health area indicator numerators with all programIndicators",
        usage=usage)
    parser.add_argument('-s', dest='server', action='store', help="Server URL without /api/ e.g. -s=data.psi-mis.org")
    parser.add_argument('-u', dest='username', action='store', help="DHIS2 username")
    parser.add_argument('-p', dest='password', action='store', help="DHIS2 password")
    parser.add_argument('-d', dest='debug', action='store_true', default=False, required=False,
                        help="Writes more info in log file")

    return parser.parse_args()


def create_numerator(programindicators_uid_list):
    p_uids = programindicators_uid_list
    numerator = ""
    if len(p_uids) > 0:
        numerator = 'I{{{}}}'.format('} + I{'.join(p_uids))
    return numerator


def dump_to_file(data):
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = "healtharea_indicators_backup_{}.json".format(ts)
    with open(filename, 'w') as out:
        json.dump(data, out, indent=4)
    logger.info("Before state backed up to \033[1m{}\033[0m".format(filename))


def main():
    args = parse_args()
    setup_logger()

    api = Api(server=args.server, username=args.username, password=args.password)

    if '.psi-mis.org' not in args.server and '.hnqis.org' not in args.server:
        logger.warn("This script is intended only for *.psi-mis.org or *.hnqis.org")
        sys.exit(0)

    indicators = {}
    backup_indicators = []
    container = []

    for ha in HEALTH_AREAS:

        # VMMC splits do not have their own HA
        if ha == 'VMMC':
            p1 = {
                'paging': False,
                'filter': [
                    'name:like:HNQIS - {}'.format(ha),
                    'name:$like:count',
                    'program.name:!like:v1'  # don't get v1 programIndicators
                ],
                'fields': '[id,name]'
            }
        else:
            p1 = {
                'paging': False,
                'filter': [
                    'name:like:HNQIS - {} count'.format(ha),
                    'program.name:!like:v1'  # don't get v1 programIndicators
                ],
                'fields': '[id,name]'
            }
        data1 = api.get('programIndicators', params=p1).json()
        pi_uids = [p['id'] for p in data1['programIndicators']]

        p2 = {
            'paging': False,
            'filter': ['name:eq:HNQIS - {} count'.format(ha)],
            'fields': ':owner'
        }
        data2 = api.get('indicators', params=p2).json()
        backup_indicators.append(data2['indicators'])

        if ha == 'VMMC':
            p3 = {
                'paging': False,
                'filter': [
                    'shortName:like: HNQIS {}'.format(ha),
                    'name:!like:v1'
                ],
                'fields': 'id,name'
            }
        else:
            p3 = {
                'paging': False,
                'filter': [
                    'shortName:$like: HNQIS {}'.format(ha),  # 2.30 would need to change filters
                    'name:!like:v1'
                ],
                'fields': 'id,name'
            }
        data3 = api.get('programs', params=p3).json()
        no_of_programs = len(data3['programs'])

        if no_of_programs != len(pi_uids):
            print(u"\033[1mWarning\033[1m\033[0m - number of {} programs ({}) "
                  u"does not match number of 'count' programIndicators ({})!".format(ha, no_of_programs, len(pi_uids)))
            print("\n".join([x['name'] for x in data3['programs']]))

        if len(data2['indicators']) == 1:
            i = data2['indicators'][0]
            i['numerator'] = create_numerator(pi_uids)
            container.append(i)
            print(u'  \033[1m{}\033[0m - Added {} programIndicators to numerator of indicator "{}"'.format(ha, len(pi_uids), i['name']))

        elif len(data2['indicators']) > 1:
            print(u"\033[1mMore than one indicator found for health area {}\033[0m".format(ha))
        elif len(pi_uids) != 0:
            print(u"\033[1mNo indicator found for health area {}\033[0m".format(ha))

    dump_to_file(backup_indicators)
    indicators['indicators'] = container

    print(u"Posting updated programindicators to \033[1m{}\033[0m...".format(args.server))
    time.sleep(3)

    api.post('metadata', params={'importMode': 'COMMIT', 'preheatCache': False}, data=indicators)


if __name__ == "__main__":
    main()
