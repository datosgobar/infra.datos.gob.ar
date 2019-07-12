import pytest
from django.contrib.auth.models import User


@pytest.fixture
def user():
    return User.objects.create_user('test_user', 'test_P4ssw0rd123123')
