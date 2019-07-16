#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from dhis2 import Api, setup_logger, logger

THRESHOLD = 1
ORDER_FORWARD = 'FEkGksxhOpH'
OVERALL_SCORE = 'Y8Nmpp7RhXw'


def parse_args():
    usage = "hnqis-scan-mismatches [-s] [-u] [-p] -x" \
            "\n\n\033[1mExample:\033[0m " \
            "\nhnqis-scan-mismatches -s=data.psi-mis.org -u=admin -p=district -x"
    parser = argparse.ArgumentParser(
        description="Scan mismatches of Scores > 1 value", usage=usage)
    parser.add_argument('-s', dest='server', action='store',
                        help="DHIS2 server URL without /api/ e.g. -s=play.dhis2.org/demo")
    parser.add_argument('-x', dest='fix_values', action='store_true', default=False, required=False,
                        help="Fix events by overwriting _Overall Score with 0CS-100 score + resetting _Order Forward to 9999")
    parser.add_argument('-u', dest='username', action='store', help="DHIS2 username")
    parser.add_argument('-p', dest='password', action='store', help="DHIS2 password")
    parser.add_argument('-d', dest='debug', action='store_true', default=False, required=False,
                        help="Writes more info in log file")

    return parser.parse_args()


def fix_event(event, root_compscores):
    """Adjust data values: overwrite _Overall Score with 0CS-100 value and set order forward to be 9999"""
    datavalues = event['dataValues']
    for i in range(len(datavalues)):
        if datavalues[i]['dataElement'] == ORDER_FORWARD:
            event['dataValues'][i]['value'] = '9999'
        if datavalues[i]['dataElement'] == OVERALL_SCORE:
            event['dataValues'][i]['value'] = [x['value'] for x in datavalues if x['dataElement'] in root_compscores][0]
    return event


def analyze_event(program, event, root_compscores):
    """Analyze if event needs to be fixed"""
    x = [dv['value'] for dv in event['dataValues'] if dv['dataElement'] == OVERALL_SCORE]
    y = [dv['value'] for dv in event['dataValues'] if dv['dataElement'] in root_compscores]
    if x and y:
        n1 = float(x[0])
        n2 = float(y[0])
        diff = abs(n1-n2)
        if diff > THRESHOLD:
            print(u"{},{},{},{},{},{},{}".format(event['eventDate'], program['id'], program['name'], event['event'], n1, n2, diff))
            return event['event']


def main():
    args = parse_args()
    setup_logger()

    api = Api(server=args.server, username=args.username, password=args.password)
    p = {
        'paging': False,
        'filter': 'name:like:HNQIS',
        'fields': 'id,name'
    }
    programs = api.get('programs', params=p)
    print("event_date,program,name,event,_OverallScore,0CS-100,diff")
    fix_them = []

    csparams = {
        'filter': ['shortName:like:.0CS-100', 'name:!ilike:_DEL'],
        'paging': False,
        'fields': 'id'
    }
    root_compscores = [x['id'] for x in api.get('dataElements', params=csparams).json()['dataElements']]

    for p in programs['programs']:
        params = {
            'program': p['id'],
            'skipPaging': True,
            'fields': '[*]'
        }
        events = api.get('events', params=params).json()
        for event in events['events']:
            if analyze_event(p, event, root_compscores):
                fix_them.append(event)

    if fix_them and args.fix_values:
        logger.info(u"Fixing those events and resetting _Order Forward...")
        for i, e in enumerate(fix_them, 1):
            fixed = fix_event(e, root_compscores)
            logger.info(u"[{}/{}] Pushing event {}...".format(i, len(fix_them), e['event']))
            api.put('events/{}'.format(e['event']), data=fixed)
    else:
        logger.warn(u"Not fixing events")

if __name__ == '__main__':
    main()
