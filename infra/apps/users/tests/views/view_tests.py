import pytest
from django.test import Client


CLIENT = Client()
pytestmark = pytest.mark.django_db


def test_home_login_required():
    response = CLIENT.get('/')
    assert response.status_code == 302


def test_home_ok_if_logged_in(user):
    CLIENT.force_login(user)
    response = CLIENT.get('/')
    assert response.status_code == 200


def test_username_shows_if_user_is_logged_in(user):
    CLIENT.force_login(user)
    response = CLIENT.get('/')
    assert user.username in response.content.decode('utf-8')
