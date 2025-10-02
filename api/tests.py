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

############
# Parking Sessions
#############
def test_start_parking_session():
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    response = requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token}, json={"licenseplate": "test"})
    assert(response.status_code == 201)
    assert(response.text == "Session started for: test")

def test_start_parking_session_same_licence_plate():
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    response = requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token}, json={"licenseplate": "test"})
    assert(response.status_code == 400)
    assert(response.text == "Cannot start a session when another sessions for this licesenplate is already started.")

def test_stop_parking_already_stopped():
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    response = requests.post("http://localhost:8000/parking-lots/1/sessions/stop", headers= {"Authorization": token}, json={"licenseplate": "86-JH-BZV"})
    assert(response.status_code == 400)
    assert(response.text == "Cannot stop a not started session.")

def test_stop_parking_session_another_user():
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token1 = response.json()["session_token"]
    response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
    token2 = response.json()["session_token"]
    
    requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token1}, json={"licenseplate": "test"})
    response = requests.post("http://localhost:8000/parking-lots/1/sessions/stop", headers= {"Authorization": token2}, json={"licenseplate": "test"})
    assert(response.status_code == 401)
    assert(response.text == "Cannot stop someone else's session.")

def test_stop_parking_session_good():
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    response = requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token}, json={"licenseplate": "test"})
    response = requests.post("http://localhost:8000/parking-lots/1/sessions/stop", headers= {"Authorization": token}, json={"licenseplate": "test"})
    assert(response.status_code == 200)
    assert(response.text == "Session stopped for: test")

# Reservation Tests

def test_create_reservation_success():
    # Set
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    parkinglot = 1
    response = requests.post("http://localhost:8000/reservations", headers= {"Authorization": token}, json={
        "licenseplate": "010203",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": parkinglot
        })
    assert(response.status_code == 201)
    return

def test_create_reservation_failure():
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    parkinglot = -1
    response = requests.post("http://localhost:8000/reservations", headers= {"Authorization": token}, json={
        "licenseplate": "010203",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": parkinglot
        })
    assert(response.status_code == 201)
    return

def test_update_reservation_success():
    response = requests.post(
        "http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    return

def test_update_reservation_failure():
    return

def test_delete_reservation_success():
    return

def test_delete_reservation_failure():
    return

def test_view_reservation_success():
    return