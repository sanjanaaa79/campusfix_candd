import pytest
from app import create_app, db
from app.models import User, Complaint

@pytest.fixture
def app():
    """Create application configured for testing with in-memory SQLite database."""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
        # Seed test admin
        admin = User(name="Test Admin", email="admin@test.com", role="admin")
        admin.set_password("AdminPass123")
        db.session.add(admin)

        # Seed test student
        student = User(name="Test Student", email="student@test.com", role="student")
        student.set_password("StudentPass123")
        db.session.add(student)

        # Seed second test student (for access control checks)
        student2 = User(name="Other Student", email="other@test.com", role="student")
        student2.set_password("StudentPass123")
        db.session.add(student2)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI test runner."""
    return app.test_cli_runner()
