import os

import pytest
import requests_mock
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.test import Client

from infra.apps.catalog.models import CatalogUpload, Node
from infra.apps.catalog.models.distribution import Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


@pytest.fixture
def catalog():
    return _catalog()


@pytest.fixture
def xlsx_catalog():
    with open_catalog('catalogo-justicia_valido.xlsx') as catalog_fd:
        model = CatalogUpload(format=CatalogUpload.FORMAT_XLSX,
                              xlsx_file=File(catalog_fd),
                              node=_node())
        model.save()

    return model


@pytest.fixture
def node():
    return _node()


@pytest.fixture
def mock_request():
    return requests_mock.mock()


def _node_id():
    return 'test_id'


def _node():
    return Node.objects.get_or_create(identifier=_node_id())[0]


@pytest.fixture(scope='session', autouse=True)
def media_root():
    yield
    # Will be executed after the last test
    import shutil
    shutil.rmtree(settings.MEDIA_ROOT)
    os.mkdir(settings.MEDIA_ROOT)


@pytest.fixture
def distribution_upload():
    _catalog()  # Necesario que exista un catálogo para crear un distribution upload exitorsamente
    with open_catalog('test_data.csv') as distribution_fd:
        model = _distribution().distributionupload_set.create(file=File(distribution_fd))

    return model


def _distribution():
    model = Distribution(catalog=_node(),
                         identifier="125.1",
                         dataset_identifier="125",
                         file_name="test_data.csv")
    model.save()
    return model


@pytest.fixture
def distribution():
    _catalog()
    return _distribution()


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
                              json_file=File(catalog_fd),
                              node=_node())
        model.save()

    return model


@pytest.fixture(autouse=True)
def enable_db_access(db):
    # pylint: disable=W0613,C0103
    pass


@pytest.fixture
def catalog_dest():
    dest_dir = os.path.join(settings.MEDIA_ROOT,
                            'catalog',
                            _node_id())
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, 'data.json')

    yield dest
    if os.path.exists(dest):
        os.remove(dest)
