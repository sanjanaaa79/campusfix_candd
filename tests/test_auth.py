from app.models import User

def test_student_registration(client, app):
    """Test successful user registration creates a student in database."""
    response = client.post(
        "/register",
        data={
            "name": "Jane Doe",
            "email": "jane@campus.edu",
            "password": "Password123",
            "confirm_password": "Password123"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    with app.app_context():
        user = User.query.filter_by(email="jane@campus.edu").first()
        assert user is not None
        assert user.name == "Jane Doe"
        assert user.role == "student"
        assert user.check_password("Password123")

def test_duplicate_registration_fails(client, app):
    """Test registering with an existing email fails gracefully."""
    response = client.post(
        "/register",
        data={
            "name": "Duplicate Student",
            "email": "student@test.com",  # Already seeded in conftest
            "password": "Password123",
            "confirm_password": "Password123"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"already exists" in response.data

def test_password_mismatch(client):
    """Test password confirmation mismatch."""
    response = client.post(
        "/register",
        data={
            "name": "Mismatched Pass",
            "email": "mismatch@campus.edu",
            "password": "Password123",
            "confirm_password": "DifferentPassword"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

def test_login_success_student(client):
    """Test successful login for student user."""
    response = client.post(
        "/login",
        data={
            "email": "student@test.com",
            "password": "StudentPass123"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Welcome back, Test Student" in response.data
    # Should be redirected to student dashboard
    assert b"Student Portal" in response.data

def test_login_success_admin(client):
    """Test successful login for administrator user."""
    response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "AdminPass123"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Campus Operations Dashboard" in response.data

def test_invalid_login_credentials(client):
    """Test failed login with wrong password."""
    response = client.post(
        "/login",
        data={
            "email": "student@test.com",
            "password": "WrongPassword!"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_logout(client):
    """Test logout clears session."""
    client.post(
        "/login",
        data={"email": "student@test.com", "password": "StudentPass123"},
        follow_redirects=True
    )
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"logged out" in response.data
