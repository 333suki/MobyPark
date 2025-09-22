import pytest
import requests

def test_login():
    response = requests.post(url="http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
    assert response.status_code == 401
