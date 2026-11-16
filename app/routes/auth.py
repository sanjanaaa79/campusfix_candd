import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from app.models import db, User

auth_bp = Blueprint("auth", __name__)

def login_required(view):
    """Decorator to require login for a route."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    """Decorator to require admin role for a route."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            flash("Administrator login required.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        user = db.session.get(User, user_id)
        if not user or user.role != "admin":
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for("student.dashboard"))
        return view(**kwargs)
    return wrapped_view

def student_required(view):
    """Decorator to require student role (or redirect admin)."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            return redirect(url_for("auth.login"))
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return view(**kwargs)
    return wrapped_view

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle student registration."""
    # If already logged in, redirect to respective dashboard
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard" if session.get("user_role") == "admin" else "student.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html", name=name, email=email)

        if len(name) < 2:
            flash("Name must be at least 2 characters long.", "danger")
            return render_template("register.html", name=name, email=email)

        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template("register.html", name=name, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html", name=name, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", name=name, email=email)

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        # Create student user
        new_user = User(
            name=name,
            email=email,
            role="student"
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate both students and administrators."""
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard" if session.get("user_role") == "admin" else "student.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", email=email)

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html", email=email)

        # Session setup
        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_email"] = user.email
        session["user_role"] = user.role
        session.permanent = remember

        flash(f"Welcome back, {user.name}!", "success")

        # Redirect according to role
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)

        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    """Log the current user out."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("index"))
