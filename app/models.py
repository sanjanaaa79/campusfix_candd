from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model supporting both Student and Admin roles."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")  # 'student' or 'admin'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to complaints
    complaints = db.relationship(
        "Complaint", 
        backref="author", 
        lazy="select", 
        cascade="all, delete-orphan",
        order_by="desc(Complaint.created_at)"
    )

    def set_password(self, password: str):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Complaint(db.Model):
    """Complaint model for tracking campus maintenance issues."""
    __tablename__ = "complaints"

    # Permitted values
    CATEGORIES = [
        "Electrical",
        "Plumbing",
        "Wi-Fi & Internet",
        "Furniture",
        "Cleanliness",
        "Classroom Equipment",
        "Water Supply",
        "Other"
    ]
    PRIORITIES = ["Low", "Medium", "High"]
    STATUSES = ["Pending", "In Progress", "Resolved"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(20), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        """Serialize complaint to dictionary for APIs and views."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "author_name": self.author.name if self.author else "Unknown",
            "author_email": self.author.email if self.author else "Unknown",
            "title": self.title,
            "category": self.category,
            "location": self.location,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M") if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Complaint #{self.id} '{self.title}' [{self.status}]>"
