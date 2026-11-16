import os
from flask import Flask, render_template, session, g
from dotenv import load_dotenv
from config import config_by_name
from app.models import db, User

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    """Application factory for CampusFix."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Global context processor to make current_user available in templates
    @app.context_processor
    def inject_current_user():
        user_id = session.get("user_id")
        current_user = None
        if user_id:
            current_user = db.session.get(User, user_id)
        return dict(current_user=current_user)

    # Landing page route
    @app.route("/")
    def index():
        return render_template("index.html")

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    # Auto-create tables in development mode
    with app.app_context():
        db.create_all()

    # CLI command: flask init-admin
    @app.cli.command("init-admin")
    def init_admin():
        """Initialize or update an administrator account from environment variables."""
        admin_email = os.getenv("ADMIN_EMAIL", "admin@campusfix.edu").strip().lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin@12345")
        admin_name = os.getenv("ADMIN_NAME", "CampusFix Administrator").strip()

        with app.app_context():
            user = User.query.filter_by(email=admin_email).first()
            if user:
                user.name = admin_name
                user.role = "admin"
                user.set_password(admin_password)
                db.session.commit()
                print(f"[SUCCESS] Admin user '{admin_email}' updated successfully.")
            else:
                user = User(
                    name=admin_name,
                    email=admin_email,
                    role="admin"
                )
                user.set_password(admin_password)
                db.session.add(user)
                db.session.commit()
                print(f"[SUCCESS] Admin user '{admin_email}' created successfully.")

    return app
