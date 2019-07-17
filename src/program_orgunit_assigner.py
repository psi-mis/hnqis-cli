#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
from copy import deepcopy

from dhis2 import Api, setup_logger, logger, load_csv, is_valid_uid
from six import iteritems


def parse_args():
    usage = "hnqis-program-orgunit [-s] [-u] [-p] -c [-a]" \
            "\n\n\033[1mExample:\033[0m " \
            "\nhnqis-program-orgunit -s=data.psi-mis.org -u=admin -p=district -c=/path/to/file.csv -a" \
            "\n\n\033[1mCSV file structure:\033[0m         " \
            "\norgunit     | <programUID1> | <programUID2> " \
            "\n------------|---------------|---------------" \
            "\n<orgunitUID>| yes           | no            " \
            "\n                                            "
    parser = argparse.ArgumentParser(
        description="Assign OrgUnits to Programs sourced from CSV file", usage=usage)
    parser.add_argument('-s', dest='server', action='store', help="Server URL without /api/ e.g. -s=data.psi-mis.org")
    parser.add_argument('-c', dest='source_csv', action='store', help="CSV file path", required=True)
    parser.add_argument('-a', dest='append_orgunits', action='store_true', help="Append Orgunit to existing",
                        default=False, required=False)
    parser.add_argument('-u', dest='username', action='store', help="DHIS2 username")
    parser.add_argument('-p', dest='password', action='store', help="DHIS2 password")
    parser.add_argument('-d', dest='debug', action='store_true', default=False, required=False,
                        help="Writes more info in log file")

    return parser.parse_args()


def validate_csv(data):
    if not data:
        raise ValueError(" CSV not valid (empty?)")

    if not data[0].get('orgunit', None):
        raise ValueError(u"+++ CSV not valid: CSV must have 'orgunit' header")

    if len(data[0]) <= 1:
        raise ValueError(u"+++ No programs found in CSV")

    orgunit_uids = [ou['orgunit'] for ou in data]
    if len(orgunit_uids) != len(set(orgunit_uids)):
        raise ValueError(u"Duplicate Orgunits (rows) found in the CSV")

    for ou in orgunit_uids:
        if not is_valid_uid(ou):
            raise ValueError(u"OrgUnit {} is not a valid UID in the CSV".format(ou))

    for row in data:
        for p in row.keys():
            if not is_valid_uid(p) and p != 'orgunit':
                raise ValueError(u"Program {} is not a valid UID in the CSV".format(p))
    return True


def get_program_orgunit_map(data):
    program_orgunit_map = {}
    # pmap = {
    #  "programuid":["orgunitid1", ...],
    # }
    for row in data:
        for k, v in iteritems(row):
            if k != 'orgunit' and v.lower().strip() == 'yes':
                if k not in program_orgunit_map:
                    program_orgunit_map[k] = list()
                program_orgunit_map[k].append(row['orgunit'])
    return program_orgunit_map


def set_program_orgunits(program, orgunit_list, append_orgunits):
    program_copy = deepcopy(program)
    if append_orgunits:
        tmp = program_copy.get('organisationUnits', None)
        if tmp is None:
            tmp = []
        else:
            # removing orgunits that will be added again later to avoid duplicates
            tmp[:] = [p for p in tmp if p['id'] not in orgunit_list]
    else:
        tmp = []
    for ou in orgunit_list:
        tmp.append({"id": ou})
    program_copy['organisationUnits'] = tmp
    return program_copy


def main():
    args = parse_args()
    setup_logger()

    api = Api(server=args.server, username=args.username, password=args.password)

    data = list(load_csv(args.source_csv))
    validate_csv(data)

    programs_csv = [h.strip() for h in data[0] if h != 'orgunit']
    if not programs_csv:
        raise ValueError('No programs found')
    params_get = {
        'fields': 'id',
        'paging': False
    }
    programs_server = [p['id'] for p in api.get('programs', params=params_get).json()['programs']]
    for p in programs_csv:
        if p not in programs_server:
            logger.error(u"Program {0} is not a valid program: {1}/programs/{0}.json".format(p, api.api_url))

    program_orgunit_map = get_program_orgunit_map(data)
    metadata_payload = []
    final = {}
    for program_uid, orgunit_list in iteritems(program_orgunit_map):
        params_get = {'fields': ':owner'}
        program = api.get('programs/{}'.format(program_uid), params=params_get).json()
        updated = set_program_orgunits(program, orgunit_list, args.append_orgunits)
        metadata_payload.append(updated)

        with open('backup_{}.json'.format(program_uid), 'w') as f:
            json.dump(program, f, indent=4)

        print(
            u"[{}] - Assigning \033[1m{} (total: {})\033[0m "
            u"OrgUnits to Program \033[1m{}\033[0m...".format(args.server,
                                                              len(orgunit_list),
                                                              len(program['organisationUnits']),
                                                              program['name']))

        final['programs'] = [updated]
        params_post = {
            "mergeMode": "REPLACE",
            "strategy": "UPDATE"
        }
        api.post(endpoint='metadata', params=params_post, data=final)


if __name__ == "__main__":
    main()
