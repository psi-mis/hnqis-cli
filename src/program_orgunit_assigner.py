import argparse
import sys
from collections import Counter

import unicodecsv as csv

from __init__ import init_logger, log_start_info, Dhis, valid_uid, CsvException


def parse_args():
    usage = "hnqis-program-orgunit [-s] [-u] [-p] -c" \
            "\n\n\033[1mExample:\033[0m " \
            "\nhnqis-program-orgunit -s=data.psi-mis.org -u=admin -p=district -c=/path/to/file.csv" \
            "\n\n\033[1mCSV file structure:\033[0m         " \
            "\norgunit     | <programUID1> | <programUID2> " \
            "\n------------|---------------|---------------" \
            "\n<orgunitUID>| yes           | no            " \
            "\n                                            "
    parser = argparse.ArgumentParser(
        description="Assign OrgUnits to Programs sourced from CSV file (replaces orgunits)", usage=usage)
    parser.add_argument('-s', dest='server', action='store', help="Server URL without /api/ e.g. -s=data.psi-mis.org")
    parser.add_argument('-c', dest='source_csv', action='store', help="CSV file path", required=True)
    parser.add_argument('-u', dest='username', action='store', help="DHIS2 username")
    parser.add_argument('-p', dest='password', action='store', help="DHIS2 password")
    parser.add_argument('-d', dest='debug', action='store_true', default=False, required=False,
                        help="Writes more info in log file")

    return parser.parse_args()


def validate_csv(data):
    if not data:
        raise CsvException(" CSV not valid (empty?)")

    if not data[0].get('orgunit', None):
        raise CsvException("+++ CSV not valid: CSV must have 'orgunit' header")

    if len(data[0]) <= 1:
        raise CsvException("+++ No programs found in CSV")

    orgunit_uids = [ou['orgunit'] for ou in data]
    if len(orgunit_uids) != len(set(orgunit_uids)):
        raise CsvException("Duplicate Orgunits (rows) found in the CSV")

    for ou in orgunit_uids:
        if not valid_uid(ou):
            raise CsvException("OrgUnit {} is not a valid UID in the CSV".format(ou))

    for row in data:
        for p in row.keys():
            if not valid_uid(p) and p != 'orgunit':
                raise CsvException("Program {} is not a valid UID in the CSV".format(p))
    return True


def get_program_orgunit_map(data):
    program_orgunit_map = {}
    # pmap = {
    #  "programuid":["orgunitid1", ...],
    # }
    for row in data:
        for k, v in row.iteritems():
            if k != 'orgunit' and v.lower().strip() == 'yes':
                if k not in program_orgunit_map:
                    program_orgunit_map[k] = list()
                program_orgunit_map[k].append(row['orgunit'])
    return program_orgunit_map


def set_program_orgunits(program, orgunit_list):
    tmp = []
    for ou in orgunit_list:
        tmp.append({"id": ou})
    program['organisationUnits'] = tmp
    return program


def main():
    args = parse_args()
    init_logger(args.debug)
    log_start_info(__file__)

    api = Dhis(server=args.server, username=args.username, password=args.password)

    """
    if '.psi-mis.org' not in args.server:
        log_info("This script is intended only for *.psi-mis.org")
        sys.exit()
    """

    with open(args.source_csv) as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        validate_csv(data)

    program_uids = [h.strip() for h in data[0] if h != 'orgunit']
    for p in program_uids:
        api.get('programs/{}'.format(p))

    program_orgunit_map = get_program_orgunit_map(data)
    metadata_payload = []
    final = {}
    for program_uid, orgunit_list in program_orgunit_map.iteritems():
        params_get = {'fields': ':owner'}
        program = api.get('programs/{}'.format(program_uid), params=params_get)
        updated = set_program_orgunits(program, orgunit_list)
        metadata_payload.append(updated)
        print("[{}] - Assigning \033[1m{}\033[0m OrgUnits to Program \033[1m{}\033[0m...".format(args.server, len(orgunit_list), program['name']))

    final['programs'] = metadata_payload
    params_post = {
        "mergeMode": "REPLACE",
        "strategy": "UPDATE"
    }
    api.post(endpoint='metadata', params=params_post, payload=final)


if __name__ == "__main__":
    main()
