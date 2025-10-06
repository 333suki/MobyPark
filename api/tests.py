import pytest
import requests
import time

# ##################
# # User registering
# ##################
# def test_register_new_account():
#     response = requests.post("http://localhost:8000/register", json={"username": "admindoe", "password": "password123", "name": "John Admin Doe"})
#     assert(response.status_code == 201)
#     assert(response.text == "User created")

# def test_register_account_exists():
#     response = requests.post("http://localhost:8000/register", json={"username": "johndoe", "password": "password123", "name": "John Doe"})
#     assert(response.status_code == 409)
#     assert(response.text == "Username already taken")

# def test_register_empty_body():
#     response = requests.post("http://localhost:8000/register")
#     assert(response.status_code == 400)
#     assert(response.text == "Empty request body")

# def test_register_empty_body_catch_error():
#     with pytest.raises(requests.exceptions.ConnectionError):
#         response = requests.post("http://localhost:8000/register")
#         assert (response.status_code == 400)

# ############
# # User login
# ############
# def test_login_success():
#     response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
#     assert(response.status_code == 200)
#     assert(response.json()["message"] == "User logged in")

# def test_login_wrong_password():
#     response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "123456"})
#     assert(response.status_code == 401)
#     assert(response.text == "Invalid credentials")

# def test_login_empty_body():
#     response = requests.post("http://localhost:8000/login")
#     assert(response.status_code == 400)
#     assert(response.text == "Empty request body")

# #############
# # User Logout
# #############
# def test_user_logout_success():
#     response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
#     token = response.json()["session_token"]
#     response = requests.get("http://localhost:8000/logout", headers= {"Authorization": token})
#     assert(response.status_code == 200)
#     assert(response.text == "User logged out")

# def test_user_logout_invalid_token():
#     # response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
#     # token = response.json()["session_token"]
#     response = requests.get("http://localhost:8000/logout")
#     assert(response.status_code == 401)
#     assert(response.text == "Invalid session token")

# #########################
# # User Account Management
# #########################
# def test_user_update_success():
#     response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
#     token = response.json()["session_token"]
#     response = requests.put("http://localhost:8000/profile", headers= {"Authorization": token}, json={"username": "johndoe2", "password": "password321"})
#     assert(response.status_code == 200)
#     assert(response.text == "User updated succesfully")

# def test_user_update_unauthorized():
#     response = requests.put("http://localhost:8000/profile", json={"username": "johndoe2", "password": "password321"})
#     assert(response.status_code == 401)
#     assert(response.text == "Unauthorized: Invalid or missing session token")

# ##################
# # Parking Sessions
# ##################
# def test_start_parking_session():
#     response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
#     token = response.json()["session_token"]
#     response = requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token}, json={"licenseplate": "test"})
#     assert(response.status_code == 201)
#     assert(response.text == "Session started for: test")

# def test_start_parking_session_same_licence_plate():
#     response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
#     token = response.json()["session_token"]
#     response = requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token}, json={"licenseplate": "test"})
#     assert(response.status_code == 400)
#     assert(response.text == "Cannot start a session when another sessions for this licesenplate is already started.")

# def test_stop_parking_already_stopped():
#     response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
#     token = response.json()["session_token"]
#     response = requests.post("http://localhost:8000/parking-lots/1/sessions/stop", headers= {"Authorization": token}, json={"licenseplate": "86-JH-BZV"})
#     assert(response.status_code == 400)
#     assert(response.text == "Cannot stop a not started session.")

# def test_stop_parking_session_another_user():
#     response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
#     token1 = response.json()["session_token"]
#     response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
#     token2 = response.json()["session_token"]
    
#     requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token1}, json={"licenseplate": "test"})
#     response = requests.post("http://localhost:8000/parking-lots/1/sessions/stop", headers= {"Authorization": token2}, json={"licenseplate": "test"})
#     assert(response.status_code == 401)
#     assert(response.text == "Cannot stop someone else's session.")

# def test_stop_parking_session_good():
#     response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
#     token = response.json()["session_token"]
#     response = requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token}, json={"licenseplate": "test"})
#     response = requests.post("http://localhost:8000/parking-lots/1/sessions/stop", headers= {"Authorization": token}, json={"licenseplate": "test"})
#     assert(response.status_code == 200)
#     assert(response.text == "Session stopped for: test")

# ############
# # Parking Lots
# #############
# def test_add_parking_lot_admin():
#     response = requests.post("http://localhost:8000/login", json={"username": "admindoe", "password": "password123"})
#     token = response.json()["session_token"]
#     response = requests.post("http://localhost:8000/parking-lots", headers={"Authorization": token}, json={
#         "name": "Test Admin Garage",
#         "location": "Test District",
#         "address": "Teststraat 123, 1000 AB Testcity",
#         "capacity": 250,
#         "reserved": 50,
#         "tariff": 2.5,
#         "daytariff": 15,
#         "coordinates": {"lat": 52.1234, "lng": 5.4321}
#     })
#     assert(response.status_code == 201)
#     assert("new_lid" in response.json())

def test_get_parking_lots_user():
    response = requests.post("http://localhost:8000/login", json={"username": "johndoe", "password": "password123"})
    token = response.json()["session_token"]
    response = requests.post("http://localhost:8000/parking-lots/1/sessions/start", headers= {"Authorization": token}, json={"licenseplate": "test"})
    response = requests.post("http://localhost:8000/parking-lots/1/sessions/stop", headers= {"Authorization": token}, json={"licenseplate": "test"})
    assert(response.status_code == 200)
    assert(response.text == "Session stopped for: test")

# Reservation Tests

def test_create_reservation_correct_data():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Reservation data
    reservation_data = {
        "licenseplate": "010203",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": "1"
    }
    
    # Get response
    response = requests.post(
        "http://localhost:8000/reservations", 
        headers= {"Authorization": token}, 
        json=reservation_data
        )
    
    assert(response.status_code == 201)
    

def test_create_reservation_wrong_data():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Reservation data with failty data
    reservation_data = {
        "licenseplate": "010203",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": "-1"
    }
    
    # Get response
    response = requests.post(
        "http://localhost:8000/reservations", 
        headers= {"Authorization": token}, 
        json=reservation_data
        )
    
    assert(response.status_code == 401)

def test_create_reservation_missing_data():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Reservation data with missing field
    reservation_data = {
        "licenseplate": "010203",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
    }
    
    # Get response
    response = requests.post(
        "http://localhost:8000/reservations", 
        headers= {"Authorization": token}, 
        json=reservation_data
        )
    
    assert(response.status_code == 401)

def test_update_reservation_success():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Reservation data
    reservation_data = {
        "licenseplate": "010203",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": "1"
    }
    
    # Get response, create reservation
    response = requests.post(
        "http://localhost:8000/reservations", 
        headers= {"Authorization": token}, 
        json=reservation_data
        )
    
    reservation_id = response.json()["reservation"]["id"]
    
    updated_data = {
        "licenseplate": "010203",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": "2"
    }
    
    # Get response
    response = requests.put(
        f"http://localhost:8000/reservations/{reservation_id}", 
        headers= {"Authorization": token}, 
        json=updated_data
        )
    
    assert(response.status_code == 200)

def test_update_reservation_failure():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Random data    
    updated_data = {
        "licenseplate": "non_existent",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": "-2" # falty parking lot
    }
    
    # Get response
    response = requests.put(
        f"http://localhost:8000/reservations/999999", 
        headers= {"Authorization": token}, 
        json=updated_data
        )
    
    assert(response.status_code == 404)

def test_delete_reservation_success():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Reservation data
    reservation_data = {
        "licenseplate": "010203",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": "1"
    }
    
    # Get response, create reservation
    response = requests.post(
        "http://localhost:8000/reservations", 
        headers= {"Authorization": token}, 
        json=reservation_data
        )
    reservation_id = response.json()["reservation"]["id"]
    
    # Delete reservation
    response = requests.delete(
        f"http://localhost:8000/reservations/{reservation_id}", 
        headers={"Authorization": token}
        )
    
    assert(response.status_code == 200)
    
    

def test_delete_reservation_failure():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Delete non-existent reservation
    response = requests.delete(
        f"http://localhost:8000/reservations/77777", 
        headers={"Authorization": token}
        )
    
    assert(response.status_code == 200)

def test_view_reservation_success():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Make a reservation
    create_data = {
        "licenseplate": "VIEW123",
        "startdate": "01/01/2025",
        "enddate": "12/12/2025",
        "parkinglot": "1"
    }
    
    response = requests.post(
        "http://localhost:8000/reservations", 
        headers={"Authorization": token}, 
        json=create_data
    )
    
    reservation_id = response.json()["reservation"]["id"]
    response = requests.get(
        f"http://localhost:8000/reservations/{reservation_id}", 
        headers={"Authorization": token}
    )
    
    assert(response.status_code == 200)
    
def test_view_reservation_failure():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    response = requests.get(
        f"http://localhost:8000/reservations/9999999", 
        headers={"Authorization": token}
    )
    
    assert(response.status_code == 404)
    
# Test Billing
def test_billing_no_token():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    
    response = requests.get(
        f"http://localhost:8000/billing", 
        headers={"Authorization": ""}
    )
    
    assert(response.status_code == 404)

def test_billing_success():
    # Login
    response = requests.post("http://localhost:8000/login", json={"username": "test", "password": "test"})
    token = response.json()["session_token"]
    
    # Start new session
    requests.post(
        f"http://localhost:8000/parking-lots/1/sessions/start",
        headers={"Authorization": token},
        json={"licenseplate": "BILL001"}
    )
    
    time.sleep(2)
    
    # Stop new session to generate billing
    requests.post(
        f"http://localhost:8000/parking-lots/{parking_lot_id}/sessions/stop",
        headers={"Authorization": token},
        json={"licenseplate": "BILL001"}
    )
        
    response = requests.get(
        f"http://localhost:8000/billing", 
        headers={"Authorization": token}
    )
    
    assert(response.status_code == 200)
