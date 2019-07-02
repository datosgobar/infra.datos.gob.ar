from django.test import Client


def test_home_is_accesible():
    client = Client()
    response = client.get('/')
    assert response.status_code == 200
