import pytest
from django.test import Client
from django.urls import resolve

CLIENT = Client()
pytestmark = pytest.mark.django_db


def test_home_login_required():
    response = CLIENT.get('/')
    assert response.status_code == 302 and resolve(response.url.split("?")[0]).url_name == 'login'


def test_home_ok_if_logged_in(user):
    CLIENT.force_login(user)
    response = CLIENT.get('/')
    assert response.status_code == 302 and resolve(response.url).url_name == 'nodes'


def test_username_shows_if_user_is_logged_in(user):
    CLIENT.force_login(user)
    response = CLIENT.get(CLIENT.get('/').url)
    assert user.username in response.content.decode('utf-8')
