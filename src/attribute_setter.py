#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
from copy import deepcopy

from dhis2 import Api, setup_logger, logger, load_csv, is_valid_uid

OBJ_TYPES = {
    "categoryOptions",
    "categoryOptionCombinations",
    "categoryOptionGroups",
    "constants",
    "dataElements",
    "dataElementGroups",
    "dataSets",
    "documents",
    "indicators",
    "indicatorGroups",
    "legends",
    "options",
    "optionSets",
    "organisationUnits",
    "organisationUnitGroups",
    "programs",
    "programIndiators",
    "programStages",
    "sections",
    "sqlViews",
    "trackedEntities",
    "trackedEntityAttributes",
    "users",
    "userGroups"
}


def parse_args():
    usage = "hnqis-attribute-setting [-s] [-u] [-p] -c -t -a" \
            "\n\n\033[1mExample:\033[0m " \
            "\nhnqis-attribute-setting -s=data.psi-mis.org -u=admin -p=district -c=/path/to/file.csv -t=organisationUnits -a=pt5Ll9bb2oP" \
            "\n\n\033[1mCSV file structure:\033[0m         " \
            "\nkey     | value                             " \
            "\n--------|--------                           " \
            "\nUID     | myValue                          " \
            "\n                                            "
    parser = argparse.ArgumentParser(
        description="Post Attribute Values sourced from CSV file", usage=usage)
    parser.add_argument('-s', dest='server', action='store',
                        help="DHIS2 server URL without /api/ e.g. -s=play.dhis2.org/demo")
    parser.add_argument('-c', dest='source_csv', action='store', help="CSV file with Attribute values",
                        required=True)
    parser.add_argument('-t', dest='object_type', action='store', help="DHIS2 object type to set attribute values",
                        required=True, choices=OBJ_TYPES)
    parser.add_argument('-a', dest='attribute_uid', action='store', help='Attribute UID', required=True)
    parser.add_argument('-u', dest='username', action='store', help="DHIS2 username")
    parser.add_argument('-p', dest='password', action='store', help="DHIS2 password")
    parser.add_argument('-d', dest='debug', action='store_true', default=False, required=False,
                        help="Writes more info in log file")

    return parser.parse_args()


def validate_csv(data):
    if not data[0].get('key', None) or not data[0].get('value', None):
        raise ValueError("CSV not valid: CSV must have 'key' and 'value' as headers")

    object_uids = [obj['key'] for obj in data]
    for uid in object_uids:
        if not is_valid_uid(uid):
            raise ValueError("Object {} is not a valid UID in the CSV".format(uid))
    if len(object_uids) != len(set(object_uids)):
        raise ValueError("Duplicate Objects (rows) found in the CSV")
    return True


def create_or_update_attributevalues(obj, attribute_uid, attribute_value):
    obj_copy = deepcopy(obj)
    updated = {
        "value": attribute_value,
        "attribute": {
            "id": attribute_uid,
        }
    }
    # if no single attribute is set
    if not obj.get('attributeValues', None):
        obj_copy['attributeValues'] = [updated]
        return obj_copy

    if len(obj['attributeValues']) == 1 and attribute_uid in [x['attribute']['id'] for x in obj['attributeValues']]:
        # just one attribute matching to target UID
        obj_copy['attributeValues'] = [updated]
        return obj_copy
    else:
        # there are more than 1 attribute values.
        # extract all values except target UID (if existing) and add target value.
        old = [x for x in obj['attributeValues'] if x['attribute']['id'] != attribute_uid]
        obj_copy['attributeValues'] = old
        obj_copy['attributeValues'].append(updated)
        return obj_copy


def main():
    args = parse_args()
    setup_logger()

    api = Api(server=args.server, username=args.username, password=args.password)

    if not is_valid_uid(args.attribute_uid):
        logger.error("Attribute {} is not a valid UID".format(args.attribute_uid))

    data = list(load_csv(args.source_csv))
    validate_csv(data)

    attr_get = {'fields': 'id,name,{}Attribute'.format(args.object_type[:-1])}
    attr = api.get('attributes/{}'.format(args.attribute_uid), params=attr_get).json()
    if attr['{}Attribute'.format(args.object_type[:-1])] is False:
        logger.error("Attribute {} is not assigned to type {}".format(args.attribute_uid, args.object_type[:-1]))

    logger.info(
        "[{}] - Updating Attribute Values for Attribute \033[1m{}\033[0m for \033[1m{}\033[0m \033[1m{}\033[0m...".format(
            args.server, args.attribute_uid, len(data), args.object_type))
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        logger.warn("\033[1m{}\033[0m".format("Aborted!"))
        pass

    for i, obj in enumerate(data, 1):
        obj_uid = obj.get('key')
        attribute_value = obj.get('value')
        params_get = {'fields': ':owner'}
        obj_old = api.get('{}/{}'.format(args.object_type, obj_uid), params=params_get).json()
        obj_updated = create_or_update_attributevalues(obj=obj_old, attribute_uid=args.attribute_uid,
                                                       attribute_value=attribute_value)
        api.put('{}/{}'.format(args.object_type, obj_uid), params=None, data=obj_updated)
        logger.info(u"{}/{} - Updated AttributeValue: {} - {}: {}".format(i, len(data), attribute_value,
                                                                                        args.object_type[:-1], obj_uid))


if __name__ == "__main__":
    main()
