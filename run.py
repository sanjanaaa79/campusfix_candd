import os
import sys
from app import create_app, db
from app.models import User

app = create_app(os.getenv("FLASK_ENV", "default"))

if __name__ == "__main__":
    # Check for CLI args like: python run.py init-admin
    if len(sys.argv) > 1 and sys.argv[1] == "init-admin":
        with app.app_context():
            admin_email = os.getenv("ADMIN_EMAIL", "admin@campusfix.edu").strip().lower()
            admin_password = os.getenv("ADMIN_PASSWORD", "Admin@12345")
            admin_name = os.getenv("ADMIN_NAME", "CampusFix Administrator").strip()

            user = User.query.filter_by(email=admin_email).first()
            if user:
                user.name = admin_name
                user.role = "admin"
                user.set_password(admin_password)
                db.session.commit()
                print(f"[SUCCESS] Admin user '{admin_email}' updated successfully.")
            else:
                user = User(name=admin_name, email=admin_email, role="admin")
                user.set_password(admin_password)
                db.session.add(user)
                db.session.commit()
                print(f"[SUCCESS] Admin user '{admin_email}' created successfully.")
        sys.exit(0)

    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"[*] Starting CampusFix on http://127.0.0.1:{port} (Debug={debug})...")
    app.run(host="0.0.0.0", port=port, debug=debug)
