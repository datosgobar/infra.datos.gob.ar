import os

import pytest
import requests_mock
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.test import Client

from infra.apps.catalog.models import CatalogUpload, Node, Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


@pytest.fixture
def catalog():
    return _catalog()


@pytest.fixture
def xlsx_catalog():
    with open_catalog('catalogo-justicia.xlsx') as catalog_fd:
        model = CatalogUpload(format=CatalogUpload.FORMAT_XLSX,
                              file=File(catalog_fd),
                              node=_node())
        model.save()

    return model


@pytest.fixture
def node():
    return _node()


@pytest.fixture
def mock_request():
    return requests_mock.mock()


def _node():
    return Node.objects.get_or_create(identifier='test_id')[0]


@pytest.fixture(scope='session', autouse=True)
def media_root():
    yield
    # Will be executed after the last test
    import shutil
    shutil.rmtree(settings.MEDIA_ROOT)
    os.mkdir(settings.MEDIA_ROOT)


@pytest.fixture
def distribution():
    _catalog()
    with open_catalog('test_data.csv') as distribution_fd:
        model = Distribution(file=File(distribution_fd),
                             node=_node(),
                             identifier="125.1",
                             dataset_identifier="125",
                             file_name="test_data.csv")
        model.save()

    return model


@pytest.fixture
def admin_client():
    admin = get_user_model().objects.create_superuser('superuser', 'email@test.com', 'password')
    client = Client()
    client.login(username=admin.username, password='password')
    return client


@pytest.fixture
def logged_client():
    logged_user = _user()
    client = Client()
    client.login(username=logged_user.username, password='password')
    return client


@pytest.fixture
def user():
    return _user()


def _user():
    try:
        test_user = get_user_model().objects.get(username='user')
    except get_user_model().DoesNotExist:
        test_user = get_user_model()(username='user', email='email@test.com')
        test_user.set_password('password')
        test_user.save()
    return test_user


def _catalog():
    with open_catalog('data.json') as catalog_fd:
        model = CatalogUpload(format=CatalogUpload.FORMAT_JSON,
                              file=File(catalog_fd),
                              node=_node())
        model.save()

    return model
