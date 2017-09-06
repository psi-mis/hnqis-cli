import pytest

from src.attribute_setter import *

TEST_ATTRIBUTE_UID = 'M8fCOxtkURr'


def load_csv(file_name):
    with open(os.path.join('tests', 'csv', 'attribute_setting', file_name), 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


@pytest.fixture
def csv_file_valid():
    return load_csv('valid.csv')


def test_csv_file_valid(csv_file_valid):
    assert validate_csv(csv_file_valid)


@pytest.fixture
def csv_file_duplicates():
    return load_csv('duplicates.csv')


def test_csv_duplicate_objects(csv_file_duplicates):
    with pytest.raises(CsvException):
        validate_csv(csv_file_duplicates)


@pytest.fixture
def csv_file_no_valid_uid():
    return load_csv('no_valid_uid.csv')


def test_csv_no_valid_uid(csv_file_no_valid_uid):
    with pytest.raises(CsvException):
        validate_csv(csv_file_no_valid_uid)


@pytest.fixture
def user_with_attributevalue():
    u = {
        "created": "2015-03-31T13:31:09.324",
        "lastUpdated": "2017-09-05T18:55:58.673",
        "id": "DXyJmlo9rge",
        "firstName": "John",
        "surname": "Barnes",
        "email": "john@hmail.com",
        "userCredentials": {
            "code": "android",
            "lastUpdated": "2017-09-05T18:55:58.670",
            "id": "M0fCOxtkURr",
            "created": "2015-03-31T13:31:09.206",
            "name": "John Barnes",
            "lastLogin": "2015-03-31T13:39:21.777",
            "displayName": "John Barnes",
            "externalAuth": False,
            "externalAccess": False,
            "disabled": False,
            "passwordLastUpdated": "2015-03-31T13:31:09.206",
            "invitation": False,
            "selfRegistered": False,
            "username": "android",
            "userInfo": {
                "id": "DXyJmlo9rge"
            },
            "lastUpdatedBy": {
                "id": "xE7jOejl9FI"
            },
            "user": {
                "id": "xE7jOejl9FI"
            },
            "cogsDimensionConstraints": [],
            "catDimensionConstraints": [],
            "translations": [],
            "userGroupAccesses": [],
            "attributeValues": [],
            "userRoles": [
                {
                    "id": "Ufph3mGRmMo"
                },
                {
                    "id": "Euq3XfEIEbx"
                },
                {
                    "id": "cUlTcejWree"
                },
                {
                    "id": "DRdaVRtwmG5"
                },
                {
                    "id": "jRWSNIHdKww"
                },
                {
                    "id": "txB7vu1w2Pr"
                }
            ],
            "userAccesses": []
        },
        "attributeValues": [
            {
                "lastUpdated": "2017-09-05T18:55:58.633",
                "created": "2017-09-05T18:55:58.631",
                "value": "hello",
                "attribute": {
                    "id": TEST_ATTRIBUTE_UID
                }
            }
        ],
        "teiSearchOrganisationUnits": [],
        "organisationUnits": [
            {
                "id": "DiszpKrYNg8"
            }
        ],
        "dataViewOrganisationUnits": [
            {
                "id": "YuQRtpLP10I"
            }
        ]
    }
    return u


def test_attribute_value_updated(user_with_attributevalue):
    new_value = 'NEW123'
    updated = create_or_update_attributevalues(obj=user_with_attributevalue, attribute_value=new_value,
                                               attribute_uid=TEST_ATTRIBUTE_UID)
    assert len(updated['attributeValues']) == 1
    assert new_value in [x['value'] for x in updated['attributeValues'] if x['attribute']['id'] == TEST_ATTRIBUTE_UID]

    # assert other values have not changed
    updated.pop('attributeValues')
    pairs = zip(updated, user_with_attributevalue)
    assert any(x != y for x, y in pairs)


@pytest.fixture
def user_without_attributevalues():
    u = {
        "created": "2015-03-31T13:31:09.324",
        "lastUpdated": "2017-09-05T18:55:58.673",
        "id": "DXyJmlo9rge",
        "firstName": "John",
        "surname": "Barnes",
        "email": "john@hmail.com",
        "userCredentials": {
            "code": "android",
            "lastUpdated": "2017-09-05T18:55:58.670",
            "id": "M0fCOxtkURr",
            "created": "2015-03-31T13:31:09.206",
            "name": "John Barnes",
            "lastLogin": "2015-03-31T13:39:21.777",
            "displayName": "John Barnes",
            "externalAuth": False,
            "externalAccess": False,
            "disabled": False,
            "passwordLastUpdated": "2015-03-31T13:31:09.206",
            "invitation": False,
            "selfRegistered": False,
            "username": "android",
            "userInfo": {
                "id": "DXyJmlo9rge"
            },
            "lastUpdatedBy": {
                "id": "xE7jOejl9FI"
            },
            "user": {
                "id": "xE7jOejl9FI"
            },
            "cogsDimensionConstraints": [],
            "catDimensionConstraints": [],
            "translations": [],
            "userGroupAccesses": [],
            "attributeValues": [],
            "userRoles": [
                {
                    "id": "Ufph3mGRmMo"
                },
                {
                    "id": "Euq3XfEIEbx"
                },
                {
                    "id": "cUlTcejWree"
                },
                {
                    "id": "DRdaVRtwmG5"
                },
                {
                    "id": "jRWSNIHdKww"
                },
                {
                    "id": "txB7vu1w2Pr"
                }
            ],
            "userAccesses": []
        },
        "teiSearchOrganisationUnits": [],
        "organisationUnits": [
            {
                "id": "DiszpKrYNg8"
            }
        ],
        "dataViewOrganisationUnits": [
            {
                "id": "YuQRtpLP10I"
            }
        ]
    }
    return u


def test_attribute_new_value(user_without_attributevalues):
    new_value = 'NEW123'
    updated = create_or_update_attributevalues(obj=user_without_attributevalues, attribute_value=new_value,
                                               attribute_uid=TEST_ATTRIBUTE_UID)
    assert len(updated['attributeValues']) == 1
    assert new_value in [x['value'] for x in updated['attributeValues'] if x['attribute']['id'] == TEST_ATTRIBUTE_UID]

    # assert other values have not changed
    updated.pop('attributeValues')
    pairs = zip(updated, user_without_attributevalues)
    assert any(x != y for x, y in pairs)


@pytest.fixture
def user_added_attributevalues():
    u = {
        "created": "2015-03-31T13:31:09.324",
        "lastUpdated": "2017-09-05T18:55:58.673",
        "id": "DXyJmlo9rge",
        "firstName": "John",
        "surname": "Barnes",
        "email": "john@hmail.com",
        "userCredentials": {
            "code": "android",
            "lastUpdated": "2017-09-05T18:55:58.670",
            "id": "M0fCOxtkURr",
            "created": "2015-03-31T13:31:09.206",
            "name": "John Barnes",
            "lastLogin": "2015-03-31T13:39:21.777",
            "displayName": "John Barnes",
            "externalAuth": False,
            "externalAccess": False,
            "disabled": False,
            "passwordLastUpdated": "2015-03-31T13:31:09.206",
            "invitation": False,
            "selfRegistered": False,
            "username": "android",
            "userInfo": {
                "id": "DXyJmlo9rge"
            },
            "lastUpdatedBy": {
                "id": "xE7jOejl9FI"
            },
            "user": {
                "id": "xE7jOejl9FI"
            },
            "cogsDimensionConstraints": [],
            "catDimensionConstraints": [],
            "translations": [],
            "userGroupAccesses": [],
            "attributeValues": [],
            "userRoles": [
                {
                    "id": "Ufph3mGRmMo"
                },
                {
                    "id": "Euq3XfEIEbx"
                },
                {
                    "id": "cUlTcejWree"
                },
                {
                    "id": "DRdaVRtwmG5"
                },
                {
                    "id": "jRWSNIHdKww"
                },
                {
                    "id": "txB7vu1w2Pr"
                }
            ],
            "userAccesses": []
        },
        "attributeValues": [
            {
                "lastUpdated": "2017-09-05T18:55:58.633",
                "created": "2017-09-05T18:55:58.631",
                "value": "hello",
                "attribute": {
                    "id": TEST_ATTRIBUTE_UID
                }
            },
            {
                "lastUpdated": "2017-09-05T18:55:58.633",
                "created": "2017-09-05T18:55:58.631",
                "value": "somethingother",
                "attribute": {
                    "id": "DiszpKrYNg6"
                }
            }
        ],
        "teiSearchOrganisationUnits": [],
        "organisationUnits": [
            {
                "id": "DiszpKrYNg8"
            }
        ],
        "dataViewOrganisationUnits": [
            {
                "id": "YuQRtpLP10I"
            }
        ]
    }
    return u


def test_attribute_added_value(user_added_attributevalues):
    new_value = 'NEW123'
    updated = create_or_update_attributevalues(obj=user_added_attributevalues, attribute_value=new_value,
                                               attribute_uid=TEST_ATTRIBUTE_UID)
    assert len(updated['attributeValues']) == 2
    assert set([x['attribute']['id'] for x in updated['attributeValues']]) == {TEST_ATTRIBUTE_UID, 'DiszpKrYNg6'}
    assert new_value in [x['value'] for x in updated['attributeValues'] if x['attribute']['id'] == TEST_ATTRIBUTE_UID]

    # assert other values have not changed
    updated.pop('attributeValues')
    user_added_attributevalues.pop('attributeValues')
    pairs = zip(updated, user_added_attributevalues)
    assert any(x != y for x, y in pairs)
