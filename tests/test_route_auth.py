from unittest.mock import MagicMock

from src.database.models import User

refresh_token = None




def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    response = client.post('/api/auth/signup', json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload['user']['email'] == user.get('email')


def test_repeat_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    response = client.post('/api/auth/signup', json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    assert payload['detail'] == "Account already exists"


def test_login_user_not_confirmed_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    
    global refresh_token
    refresh_token = response.json()["refresh_token"]
    assert response.status_code == 200

def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"

def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_refresh_token(client):
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.get("/api/auth/refresh_token", headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_invalid_refresh_token(client):
    refresh_token = None
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.get("/api/auth/refresh_token", headers=headers)

    assert response.status_code == 401



def test_confirmed_email_valid_token(client, session, user, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    mock_auth_service_get_email_from_token = MagicMock(return_value=user.get('email'))
    monkeypatch.setattr("src.routes.auth.auth_service.get_email_from_token", mock_auth_service_get_email_from_token)
    response = client.get("/api/auth/confirmed_email/valid_token")
    assert response.status_code == 200
    assert response.json()["message"] == "Email confirmed"
    

def test_confirmed_email_invalid_token(client, monkeypatch):
    mock_auth_service_get_email_from_token = MagicMock(return_value="invalid@example.com")
    monkeypatch.setattr("src.routes.auth.auth_service.get_email_from_token", mock_auth_service_get_email_from_token)
    response = client.get("/api/auth/confirmed_email/invalid_token")

    assert response.status_code == 400
    assert response.json()["detail"] == "Verification error"


def test_already_confirmed_email(client, session, user, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()

    mock_auth_service_get_email_from_token = MagicMock(return_value=user.get('email'))
    monkeypatch.setattr("src.routes.auth.auth_service.get_email_from_token", mock_auth_service_get_email_from_token)

    response = client.get("/api/auth/confirmed_email/valid_token")

    assert response.status_code == 200
    assert response.json()["message"] == "Your email is already confirmed"


def test_request_valid_email(client, session, user, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post("/api/auth/request_email", json={"email": user.get('email')})

    assert response.status_code == 200
    assert response.json()["message"] == "Check your email for confirmation."


def test_request_already_email_confirmed_email(client, session, user, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post("/api/auth/request_email", json={"email": user.get('email')})

    assert response.status_code == 200
    assert response.json()["message"] == "Your email is already confirmed"





    
    
    


