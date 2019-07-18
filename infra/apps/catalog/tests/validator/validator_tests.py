# coding=utf-8
import pytest
from django.core.exceptions import ValidationError
from requests import RequestException

from infra.apps.catalog.catalog_data_validator import CatalogDataValidator
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_submit_fails_when_url_and_file_are_empty():
    validator = CatalogDataValidator()
    data_dict = {}
    with pytest.raises(ValidationError):
        validator.get_and_validate_data(data_dict)


def test_submit_fails_when_both_url_and_file_have_content():
    validator = CatalogDataValidator()
    data_dict = {'file': "something", 'url': 'string'}
    with pytest.raises(ValidationError):
        validator.get_and_validate_data(data_dict)


def test_fails_when_response_is_not_successful(node, requests_mock):
    requests_mock.get('https://fakeurl.com/data.json',
                      status_code=404)
    data_dict = {'format': 'json', 'node': node,
                 'url': 'https://fakeurl.com/data.json'}
    validator = CatalogDataValidator()
    with pytest.raises(ValidationError):
        validator.get_and_validate_data(data_dict)


def test_returns_correct_data_when_specifying_url(node, requests_mock):
    requests_mock.get('https://fakeurl.com/data.json', text="Testing text")
    data_dict = {'format': 'json', 'node': node,
                 'url': 'https://fakeurl.com/data.json'}
    validator = CatalogDataValidator()
    data = validator.get_and_validate_data(data_dict)
    assert data['file'].read() == b"Testing text"


def test_returns_correct_data_when_uploading_file(node):
    with open_catalog('simple.json') as sample:
        data_dict = {'format': 'json', 'node': node, 'file': sample}
        validator = CatalogDataValidator()
        data = validator.get_and_validate_data(data_dict)
        assert data['file'].read() == b'{"identifier": "test"}'


def test_invalid_url(node, requests_mock):
    requests_mock.get('https://fakeurl.com/data.json', exc=RequestException)
    data_dict = {'format': 'json', 'node': node,
                 'url': 'https://fakeurl.com/data.json'}
    validator = CatalogDataValidator()
    with pytest.raises(ValidationError):
        validator.get_and_validate_data(data_dict)
