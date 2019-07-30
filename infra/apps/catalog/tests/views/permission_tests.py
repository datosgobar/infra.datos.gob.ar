import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from infra.apps.catalog.mixins import UserIsNodeAdminMixin

pytestmark = pytest.mark.django_db

CATALOG_VIEWS = [
        'catalog:node',
        'catalog:add_catalog',
        'catalog:upload_success',
        'catalog:node_distributions',
        ]


def test_admin_user_can_access_all_nodes(node):
    admin = get_user_model().objects.create_superuser('superuser', 'email@test.com', 'password')
    mixin = UserIsNodeAdminMixin()
    assert mixin.check_user_is_node_admin(admin, node.id)


def test_user_cannot_modify_if_not_node_admin(user, node):
    mixin = UserIsNodeAdminMixin()
    assert not mixin.check_user_is_node_admin(user, node.id)


def test_user_can_modify_if_node_admin(user, node):
    node.admins.add(user)
    node.save()
    mixin = UserIsNodeAdminMixin()
    assert mixin.check_user_is_node_admin(user, node.id)


def test_user_cannot_modify_non_existing_node(user):
    mixin = UserIsNodeAdminMixin()
    assert not mixin.check_user_is_node_admin(user, 1)


def test_logged_in_user_can_access_node_pages(user, logged_client, node):
    node.admins.add(user)
    node.save()
    for view in CATALOG_VIEWS:
        rev = reverse(view, kwargs={'node_id': node.id})
        response = logged_client.get(rev)
        assert response.status_code == 200


def test_anonymous_user_requires_login(client, node):
    for view in CATALOG_VIEWS:
        response = client.get(reverse(view, kwargs={'node_id': node.id}))
        assert response.status_code == 302
        assert response.url.startswith('/ingresar/')


def test_superuser_can_access_all_pages(admin_client, node):
    for view in CATALOG_VIEWS:
        response = admin_client.get(reverse(view, kwargs={'node_id': node.id}))
        assert response.status_code == 200


def test_non_admin_user_gets_forbidden_http_response(node):
    new_user = get_user_model()(username='user', email='email@test.com')
    new_user.set_password('password')
    new_user.save()
    new_client = Client()
    new_client.login(username=new_user.username, password='password')
    for view in CATALOG_VIEWS:
        response = new_client.get(reverse(view, kwargs={'node_id': node.id}))
        assert response.status_code == 403
