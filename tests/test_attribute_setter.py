import pytest

from src.attribute_setter import *

TEST_ATTRIBUTE_UID = 'M8fCOxtkURr'


PATH = os.path.join('tests', 'csv', 'attribute_setter')


def test_csv_file_valid():
    f = load_csv(path=os.path.join(PATH, 'valid.csv'))
    assert validate_csv(f)


def test_csv_duplicate_objects():
    f = load_csv(path=os.path.join(PATH, 'duplicates.csv'))
    with pytest.raises(CsvException):
        validate_csv(f)


def test_csv_no_valid_uid():
    f = load_csv(path=os.path.join(PATH, 'no_valid_uid.csv'))
    with pytest.raises(CsvException):
        validate_csv(f)


def test_csv_semicolon():
    f = load_csv(path=os.path.join(PATH, 'semicolon.csv'))
    assert validate_csv(f)


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
