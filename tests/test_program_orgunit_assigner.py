import pytest

from src.program_orgunit_assigner import *

PATH = os.path.join('tests', 'csv', 'program_orgunits')


def test_csv_valid():
    f = load_csv(path=os.path.join(PATH, 'valid.csv'))
    assert validate_csv(f)


def test_csv_empty():
    with pytest.raises(CsvException):
        load_csv(path=os.path.join(PATH, 'empty.csv'))


def test_csv_no_programs():
    with pytest.raises(CsvException):
        load_csv(path=os.path.join(PATH, 'no_programs.csv'))


def test_csv_ogrunit():
    f = load_csv(path=os.path.join(PATH, 'ogrunit.csv'))
    with pytest.raises(CsvException):
        validate_csv(f)


def test_csv_duplicate_orgunits():
    f = load_csv(path=os.path.join(PATH, 'duplicate_orgunits.csv'))
    with pytest.raises(CsvException):
        validate_csv(f)


def test_csv_no_valid_orgunits():
    f = load_csv(path=os.path.join(PATH, 'no_valid_orgunits.csv'))
    with pytest.raises(CsvException):
        validate_csv(f)


def test_csv_no_valid_programs():
    f = load_csv(path=os.path.join(PATH, 'no_valid_programs.csv'))
    with pytest.raises(CsvException):
        validate_csv(f)


def test_program_orgunit_map():
    f = load_csv(path=os.path.join(PATH, 'full.csv'))
    mapped = get_program_orgunit_map(f)
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

    # assert other values have not changed
    updated_metadata.pop('organisationUnits')
    program_metadata.pop('organisationUnits')
    pairs = zip(updated_metadata, program_metadata)
    assert any(x != y for x, y in pairs)
