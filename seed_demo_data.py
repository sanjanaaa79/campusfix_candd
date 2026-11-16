"""
CampusFix - Demo Seed Script
Populates the database with sample students and campus complaints for presentation and testing.
"""
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models import User, Complaint

app = create_app()

def seed():
    with app.app_context():
        # 1. Create or ensure default Admin
        admin = User.query.filter_by(email="admin@campusfix.edu").first()
        if not admin:
            admin = User(name="Campus Admin", email="admin@campusfix.edu", role="admin")
            admin.set_password("Admin@12345")
            db.session.add(admin)

        # 2. Create Students
        student1 = User.query.filter_by(email="alex@campus.edu").first()
        if not student1:
            student1 = User(name="Alex Morgan", email="alex@campus.edu", role="student")
            student1.set_password("Password123")
            db.session.add(student1)

        student2 = User.query.filter_by(email="priya@campus.edu").first()
        if not student2:
            student2 = User(name="Priya Sharma", email="priya@campus.edu", role="student")
            student2.set_password("Password123")
            db.session.add(student2)

        db.session.commit()

        # 3. Create Sample Complaints if table empty
        if Complaint.query.count() == 0:
            now = datetime.now(timezone.utc)
            sample_complaints = [
                Complaint(
                    user_id=student1.id,
                    title="Overhead projector HDMI port broken",
                    category="Classroom Equipment",
                    location="Computer Science Building, Lab 204",
                    description="The main ceiling projector display turns magenta or disconnects when plugged into laptop HDMI cables. Classes in Lab 204 are being disrupted.",
                    priority="High",
                    status="Resolved",
                    created_at=now - timedelta(days=4),
                    updated_at=now - timedelta(days=1)
                ),
                Complaint(
                    user_id=student1.id,
                    title="Wi-Fi connectivity dropping constantly",
                    category="Wi-Fi & Internet",
                    location="Central Library, 2nd Floor Silent Zone",
                    description="The library access point keeps refusing client DHCP requests after 10-15 students connect. Very slow ping times.",
                    priority="Medium",
                    status="In Progress",
                    created_at=now - timedelta(days=2),
                    updated_at=now - timedelta(hours=6)
                ),
                Complaint(
                    user_id=student1.id,
                    title="Ceiling fan making loud rattling noise",
                    category="Electrical",
                    location="Mechanical Engineering Block, Room M-102",
                    description="The center fan has loose housing screws and vibrates violently at medium-high speeds. Potential hazard for students sitting below.",
                    priority="High",
                    status="Pending",
                    created_at=now - timedelta(hours=14),
                    updated_at=now - timedelta(hours=14)
                ),
                Complaint(
                    user_id=student2.id,
                    title="Water tap leaking continuously",
                    category="Water Supply",
                    location="Girls Hostel Block 2, 3rd Floor Washroom",
                    description="Tap #3 has a worn washer and does not close properly, leading to continuous water wastage throughout the night.",
                    priority="Medium",
                    status="In Progress",
                    created_at=now - timedelta(days=3),
                    updated_at=now - timedelta(days=1)
                ),
                Complaint(
                    user_id=student2.id,
                    title="Broken study chair with exposed nail",
                    category="Furniture",
                    location="Reading Hall B, Desk 44",
                    description="The wooden armrest is splintered and a nail is protruding. Needs replacement or repair before someone gets injured.",
                    priority="Low",
                    status="Pending",
                    created_at=now - timedelta(hours=22),
                    updated_at=now - timedelta(hours=22)
                ),
                Complaint(
                    user_id=student2.id,
                    title="Unclean corridor and overflowing trash bin",
                    category="Cleanliness",
                    location="Cafeteria Annex, West Entrance",
                    description="Food waste bins were not cleared over the weekend, creating odor and hygiene concerns.",
                    priority="Medium",
                    status="Resolved",
                    created_at=now - timedelta(days=5),
                    updated_at=now - timedelta(days=3)
                ),
            ]
            db.session.add_all(sample_complaints)
            db.session.commit()
            print("[SUCCESS] Database seeded with demo students and complaints.")
        else:
            print("[INFO] Complaints table already contains records. Skipping seed.")

if __name__ == "__main__":
    seed()
