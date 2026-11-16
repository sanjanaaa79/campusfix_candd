from app.models import db, User, Complaint

def login_user(client, email, password):
    """Helper to log in a user."""
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True
    )

def test_complaint_submission(client, app):
    """Test a logged-in student can submit a complaint."""
    login_user(client, "student@test.com", "StudentPass123")

    response = client.post(
        "/student/complaints/new",
        data={
            "title": "Broken classroom fan",
            "category": "Electrical",
            "location": "Room 101, Block A",
            "description": "The ceiling fan is making loud clicking noises and wobbling.",
            "priority": "High"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"registered successfully" in response.data

    with app.app_context():
        complaint = Complaint.query.filter_by(title="Broken classroom fan").first()
        assert complaint is not None
        assert complaint.location == "Room 101, Block A"
        assert complaint.status == "Pending"
        assert complaint.priority == "High"
        assert complaint.author.email == "student@test.com"

def test_student_isolation_and_authorization(client, app):
    """Test that a student cannot view another student's complaint (returns 403)."""
    # 1. Create a complaint owned by student 1
    with app.app_context():
        student1 = User.query.filter_by(email="student@test.com").first()
        c = Complaint(
            user_id=student1.id,
            title="Private complaint student 1",
            category="Furniture",
            location="Room 5",
            description="Broken desk",
            status="Pending"
        )
        db.session.add(c)
        db.session.commit()
        complaint_id = c.id

    # 2. Log in as other student
    login_user(client, "other@test.com", "StudentPass123")

    # 3. Try accessing student 1's complaint
    response = client.get(f"/student/complaints/{complaint_id}")
    assert response.status_code == 403
    assert b"403 Forbidden" in response.data

def test_admin_can_view_any_complaint(client, app):
    """Test that an administrator can view any student's complaint."""
    with app.app_context():
        student1 = User.query.filter_by(email="student@test.com").first()
        c = Complaint(
            user_id=student1.id,
            title="Projector glitch",
            category="Classroom Equipment",
            location="Room 303",
            description="No video signal",
            status="Pending"
        )
        db.session.add(c)
        db.session.commit()
        complaint_id = c.id

    # Log in as admin
    login_user(client, "admin@test.com", "AdminPass123")

    response = client.get(f"/student/complaints/{complaint_id}")
    assert response.status_code == 200
    assert b"Projector glitch" in response.data
    assert b"Admin Ticket Management" in response.data

def test_admin_status_and_priority_update(client, app):
    """Test that admin can update complaint status to In Progress and Resolved."""
    with app.app_context():
        student1 = User.query.filter_by(email="student@test.com").first()
        c = Complaint(
            user_id=student1.id,
            title="Water leak in restroom",
            category="Plumbing",
            location="1st Floor Restroom",
            description="Leaking pipe under sink",
            status="Pending",
            priority="Low"
        )
        db.session.add(c)
        db.session.commit()
        complaint_id = c.id

    login_user(client, "admin@test.com", "AdminPass123")

    # Update to In Progress and High priority
    response = client.post(
        f"/admin/complaints/{complaint_id}/update",
        data={"status": "In Progress", "priority": "High"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"successfully updated" in response.data

    with app.app_context():
        updated_c = db.session.get(Complaint, complaint_id)
        assert updated_c.status == "In Progress"
        assert updated_c.priority == "High"

def test_student_cannot_access_admin_dashboard(client):
    """Test that student role is denied access to admin routes."""
    login_user(client, "student@test.com", "StudentPass123")
    response = client.get("/admin/dashboard", follow_redirects=True)
    assert b"Access denied: Administrator privileges required" in response.data

def test_complaints_search_and_filter(client, app):
    """Test filtering complaints by category and status."""
    login_user(client, "student@test.com", "StudentPass123")

    with app.app_context():
        student = User.query.filter_by(email="student@test.com").first()
        c1 = Complaint(
            user_id=student.id,
            title="Wi-Fi router dead",
            category="Wi-Fi & Internet",
            location="Hall 2",
            description="No SSIDs visible",
            status="Pending"
        )
        c2 = Complaint(
            user_id=student.id,
            title="Light bulb fused",
            category="Electrical",
            location="Hall 3",
            description="Completely dark room",
            status="Resolved"
        )
        db.session.add_all([c1, c2])
        db.session.commit()

    # Filter by category Wi-Fi & Internet
    response = client.get("/student/complaints?category=Wi-Fi+%26+Internet")
    assert response.status_code == 200
    assert b"Wi-Fi router dead" in response.data
    assert b"Light bulb fused" not in response.data

    # Filter by status Resolved
    response_resolved = client.get("/student/complaints?status=Resolved")
    assert response_resolved.status_code == 200
    assert b"Light bulb fused" in response_resolved.data
    assert b"Wi-Fi router dead" not in response_resolved.data
