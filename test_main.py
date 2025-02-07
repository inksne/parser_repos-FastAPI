from fastapi.testclient import TestClient

import pytest

from main import app

client = TestClient(app)


def test_read_main_page():
    response = client.get('/')
    assert response.status_code == 200


def test_read_about_us_page():
    response = client.get('/about_us')
    assert response.status_code == 200


def test_read_register_page():
    response = client.get('/jwt/register')
    assert response.status_code == 200


def test_read_login_page():
    response = client.get('/jwt/login')
    assert response.status_code == 200


def test_login_user():
    response = client.post(
        "/jwt/login/",
        data={"username": "inksne", "password": "ink"},
    )
    try:
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
    except AssertionError:
        asser response.status_code == 400


def test_logout():
    response = client.post("/jwt/logout")
    assert response.status_code == 200
    assert response.json() == None