import pytest

import os
from src.program_orgunit_assigner import *


def load_csv(file_name):
    with open(os.path.join('tests', 'csv', file_name), 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


@pytest.fixture
def csv_file_valid():
    return load_csv('valid.csv')


def test_csv_valid(csv_file_valid):
    assert validate_csv(csv_file_valid)


@pytest.fixture
def csv_file_empty():
    return load_csv('empty.csv')


def test_csv_empty(csv_file_empty):
    with pytest.raises(CsvException):
        validate_csv(csv_file_empty)


@pytest.fixture
def csv_file_no_programs():
    return load_csv('no_programs.csv')


def test_csv_no_programs(csv_file_no_programs):
    with pytest.raises(CsvException):
        validate_csv(csv_file_no_programs)


@pytest.fixture
def csv_file_ogrunit():
    return load_csv('ogrunit.csv')


def test_csv_ogrunit(csv_file_ogrunit):
    with pytest.raises(CsvException):
        validate_csv(csv_file_ogrunit)


@pytest.fixture
def csv_file_duplicate_orgunits():
    return load_csv('duplicate_orgunits.csv')


def test_csv_duplicate_orgunits(csv_file_duplicate_orgunits):
    with pytest.raises(CsvException):
        validate_csv(csv_file_duplicate_orgunits)


@pytest.fixture
def csv_file_no_valid_orgunits():
    return load_csv('no_valid_orgunits.csv')


def test_csv_no_valid_orgunits(csv_file_no_valid_orgunits):
    with pytest.raises(CsvException):
        validate_csv(csv_file_no_valid_orgunits)


@pytest.fixture
def csv_file_no_valid_programs():
    return load_csv('no_valid_programs.csv')


def test_csv_no_valid_programs(csv_file_no_valid_programs):
    with pytest.raises(CsvException):
        validate_csv(csv_file_no_valid_programs)


@pytest.fixture
def csv_full():
    return load_csv('full.csv')


def test_program_orgunit_map(csv_full):
    mapped = get_program_orgunit_map(csv_full)
    assert set(mapped['lxAQ7Zs9VYR']) == {'HlDMbDWUmTy', 'Rp268JB6Ne4', 'cDw53Ej8rju'}
    assert set(mapped['IpHINAT79UW']) == {'cDw53Ej8rju'}
    assert set(mapped['kla3mAPgvCH']) == {'HlDMbDWUmTy', 'cDw53Ej8rju'}
    # test orgunit is not in any program
    assert 'c41XRVOYNJm' not in set([x for item in mapped.itervalues() for x in item])
    # test orgunit is in program map even though the value was ' yes' or 'YES'
    assert 'HlDMbDWUmTy' in mapped['WSGAb5XwJ3Y']
    assert 'cDw53Ej8rju' in mapped['WSGAb5XwJ3Y']


@pytest.fixture
def program_orgunit_map():
    j = {
        "VBqh0ynB2wv": [
            "HlDMbDWUmTy",
            "cDw53Ej8rju"
        ]
    }
    return j


@pytest.fixture
def program_metadata():
    p = {
        "lastUpdated": "2016-04-12T20:44:46.066",
        "id": "VBqh0ynB2wv",
        "created": "2016-03-30T20:18:31.020",
        "name": "Malaria case registration",
        "shortName": "Malaria case registration",
        "publicAccess": "rw------",
        "completeEventsExpiryDays": 0,
        "ignoreOverdueEvents": False,
        "skipOffline": False,
        "captureCoordinates": False,
        "displayFrontPageList": False,
        "enrollmentDateLabel": "Enrollment Date",
        "onlyEnrollOnce": False,
        "programType": "WITHOUT_REGISTRATION",
        "relationshipFromA": False,
        "version": 1,
        "selectIncidentDatesInFuture": False,
        "incidentDateLabel": "Incident Date",
        "displayIncidentDate": False,
        "selectEnrollmentDatesInFuture": False,
        "expiryDays": 0,
        "useFirstStageDuringRegistration": False,
        "categoryCombo": {
            "id": "p0KPaWEg3cf"
        },
        "user": {
            "id": "GOLswS44mh8"
        },
        "programTrackedEntityAttributes": [],
        "notificationTemplates": [],
        "translations": [],
        "organisationUnits": [
            {
                "id": "bVZTNrnfn9G"
            }
        ],
        "userGroupAccesses": [],
        "attributeValues": [],
        "validationCriterias": [],
        "programStages": [
            {
                "id": "pTo4uMt3xur"
            }
        ],
        "userAccesses": []
    }
    return p


def test_set_program_orgunits(program_orgunit_map, program_metadata):
    updated_metadata = set_program_orgunits(program_metadata, program_orgunit_map['VBqh0ynB2wv'])
    expected1 = {'id': 'HlDMbDWUmTy'}
    expected2 = {'id': 'cDw53Ej8rju'}
    assert expected1 in updated_metadata['organisationUnits']
    assert expected2 in updated_metadata['organisationUnits']
    assert len(updated_metadata['organisationUnits']) == 2
