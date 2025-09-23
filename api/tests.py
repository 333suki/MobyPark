import pytest
import requests

##################
# User registering
##################
def test_register_new_account():
    response = requests.post("http://localhost:8000/register", json={"username": "johndoe", "password": "password123", "name": "John Doe"})
    assert(response.status_code == 201)
    assert(response.text == "User created")

def test_register_account_exists():
    response = requests.post("http://localhost:8000/register", json={"username": "johndoe", "password": "password123", "name": "John Doe"})
    assert(response.status_code == 409)
    assert(response.text == "Username already taken")

def test_register_empty_body():
    response = requests.post("http://localhost:8000/register")
    assert(response.status_code == 400)
    assert(response.text == "Empty request body")

def test_register_empty_body_catch_error():
    with pytest.raises(requests.exceptions.ConnectionError):
        response = requests.post("http://localhost:8000/register")
        assert (response.status_code == 400)

############
# User login
#############
def test_login_success():
    response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
    assert(response.status_code == 200)
    assert(response.json()["message"] == "User logged in")

def test_login_wrong_password():
    response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "123456"})
    assert(response.status_code == 401)
    assert(response.text == "Invalid credentials")

def test_login_empty_body():
    response = requests.post("http://localhost:8000/login")
    assert(response.status_code == 400)
    assert(response.text == "Empty request body")
